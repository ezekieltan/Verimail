import re
import dns.resolver
import smtplib

def getDNS(domain):
    """Retrieves the MX records of a given domain
    
    Args:
        domain: domain of email
    Returns:
        List of MX records, sorted by priority
    """
    
    ret = []
    
    #find all records of type MX
    for rdata in dns.resolver.resolve(domain, 'MX'):
        ret.append((int(rdata.preference),str(rdata.exchange)))
        
    #sort by priority
    ret = sorted(ret, key=lambda x: x[0])
    
    return ret
def verifyRegex(email):
    """Verifies an email's validity using regex
    
    Args:
        email: email address
    Returns:
        True if email is valid, False otherwise
    """
    #email regex string from http://emailregex.com/
    regex = """(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
    
    #check if email matches regex string
    x = re.search(regex, email)
    if x:
        return True
    else:
        return False
def findExtendedCode(message):
    """get extended codes, which give more information than standard 3 digit codes
    
    Args:
        message: message from email server
    Returns:
        Extended code if found, None otherwise
    """
    
    #references:
    #https://www.iana.org/assignments/smtp-enhanced-status-codes/smtp-enhanced-status-codes.xhtml
    #https://www.usps.org/info/smtp_status.html
    #https://docs.microsoft.com/en-us/exchange/mail-flow-best-practices/non-delivery-reports-in-exchange-online/non-delivery-reports-in-exchange-online
    
    #the first digit can be 2-5. Second digit can be 0-7. Third digit varies between servers.
    regex = '[2-5]\.[0-7]\.[0-9](([0-9])?)(([0-9])?)'
    
    #find such a pattern in the message
    x = re.search(regex, message)
    if x is not None:
        #return the first match
        return x.group(0)
    else:
        return None
        
stateTranslator = {0:'na',10:'regex',20:'dns',30:'helo',40:'mail',50:'rcpt'}
def retGenerator(state, status, message, returnStateInString):
    """helper function to return output in a dictionary
    
    Args:
        state: validity of email
        status: 3 digit code
        message: server message
        returnStateInString: whether to return the state in a string if True, or integer if False
    Returns:
        Dictionary containing the state, 3 digit code, extended code and server message.
    """

    #decode bytes to string
    if(not isinstance(message, str)):
        message = message.decode('UTF-8')
        
    #get extended code from message
    extendedCode = findExtendedCode(message)
    
    #translate states to strings if asked to do so from caller
    state = stateTranslator[state] if returnStateInString else state
    
    return {'state':state, 'status':status, 'extendedCode':extendedCode, 'message':message}
def check(email, tryAllServers = False, returnStateInString = True):
    """Checks the validity of an email address
    
    Args:
        email: email address
        tryAllServers: whether to exhaust all MX records or not
        returnStateInString: whether to return the state in a string if True, or integer if False
    Returns:
        Dictionary containing the state, 3 digit code, extended code and server message.
    """

    state = 0
    status = ""
    message = ""
    
    domain = email[email.find('@') + 1:]
    
    #1. Check email is valid using regex
    regexOK = verifyRegex(email)
    
    if not regexOK:
        #1 has failed, no need to do further checks.
        return retGenerator(state,status, message, returnStateInString)
    
    #1 has succeeded, upgrade state
    state = 10 if state <=10 else state
    
    #2. get MX records of the domain
    try:
        dnses = getDNS(domain)
    except dns.resolver.NXDOMAIN as e:
        #2 has failed, no need to do further checks
        return retGenerator(state,status, message, returnStateInString)
    
    #2 has succeeded, upgrade state
    state = 20 if state <=20 else state
    
    #try on every MX record
    for mx in dnses:
        try:
            #create new SMTP instance
            smtp = smtplib.SMTP(timeout=10)
            
            #connect to the mail server
            smtp.connect(mx[1])
            
            #3. send helo command
            status, message = smtp.helo()
            if status == 250:
                #3 has succeeded, upgrade state
                state = 30 if state <=30 else state
            else:
                #3 has failed, try another MX record
                continue
            
            #4. send mail command
            status, message = smtp.mail('')
            if status == 250:
                #4 has succeeded, upgrade state
                state = 40 if state <=40 else state
            else:
                #4 has failed, no need to do further checks
                return retGenerator(state,status, message, returnStateInString)
            
            #5. Send rcpt command to check if email exists
            status, message = smtp.rcpt(email)
            if status == 250:
                #5 has succeeded, upgrade state
                state = 50 if state <=50 else state
                
                #5 has succeeded, email exists
                return retGenerator(state,status, message, returnStateInString)
            
            #5 has failed
            #quit SMTP instance
            smtp.quit()
            
            #if tryAllServers is True, keep going until all MX records are exhausted
            if(not tryAllServers):
                #if tryAllServers is False, give up and return current state
                return retGenerator(state,status, message, returnStateInString)
        except smtplib.SMTPServerDisconnected as e:
            continue
        except smtplib.SMTPConnectError as e:
            continue
            
    #return current state after all MX records have been exhausted
    return retGenerator(state,status, message, returnStateInString)
