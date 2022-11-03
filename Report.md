# INFO1112 Assignment 3 


## Task 4

*Define authentication, authorization and encryption using real world examples. In less than 150 words.*

**Authentication** is the process of verifying the identity of a user, process or request. It aims to ensure that, during an information exchange, each party is the intended and valid recipient. 

For example, providing a username and password combination for online banking is an *authentication* measure that helps the Bank to correctly identify and verify your identity. 

[CRSC NIST]: https://csrc.nist.gov/glossary/term/authentication#:~:text=Definition(s)%3A,resources%20in%20an%20information%20system.



**Authorisation** is the process of checking if a client or request has the appropriate permissions to use given resources or processes. 

To continue the bank example; After the bank has completed authentication, it would *Authorise* you to access the accounts linked with your identity. This ensures that you and only you can manage transfers of your funds. 

[Bu TechWeb]: https://www.bu.edu/tech/about/security-resources/bestpractice/auth/#:~:text=Authorization%20is%20a%20process%20by,is%20that%20is%20requesting%20access.



**Encryption** is a process that ensures only certain parties can interpret and understand a piece of information. It involves converting sensitive data to ciphertext, whereby users with a special <u>key</u> can decrypt and utilise the data. 

After successful authentication + authorisation, to send the details of your bank account to your browser, the server would encrypt the data, so that anyone listening to the communication cannot record your details and gain access to your account. Your browser then decrypts the information using a shared private key, and you can view your account details safely. 

[CloudFlare]: https://www.cloudflare.com/learning/ssl/what-is-encryption/



*Discuss what the SMTP-CRAM protocol can and cannot offers in terms of the above three*
*concepts. If it can support one aspect, briefly describe the mechanism; if it fails to support*
*one aspect, give a brief counterexample to support. In less than 150 words.*

STMP-CRAM can provide <u>some</u> level of Authentication and Encryption but has no support for Authorisation. 

**Authentication** is facilitated through the base64 challenge: 

- The client decodes and rehashes a string using a private key that is known to both parties. 
- However, this authentication is *not* mutual as there is no trusted 3rd party to allow the client to authenticate the server, thus becoming vulnerable to MITM attacks

**Encryption** is performed using HMAC-MD5 for the challenge and response.

- However, the encryption is only used to authenticate the client (from the server's perspective), and the data is sent over an unencrypted connection. 
- Thereby, through the flaws mentioned above regarding Authentication, not only can the server be imitated by an eavesdropper, but it can read the information sent from the client without having to decode it! 

**Authorisation** is not supported by SMTP-CRAM as there is no implementation of permissions in the base64 challenge / response. 

- The information transfer is also freely readable if intercepted! 




