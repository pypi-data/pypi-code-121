_A='AUTH'
import base64,hmac,smtplib
from base64 import b64encode
from smtplib import SMTPAuthenticationError,SMTPException
from localstack.utils.common import to_bytes,to_str
def base64_encode(s):A=to_str(b64encode(to_bytes(s))).strip();return A
class SMTP(smtplib.SMTP):
	def login(C,user,password):
		L='auth';G=password;F=user
		def M(challenge,user,password):A=challenge;A=base64.decodestring(A);B=user+' '+hmac.HMAC(password,A).hexdigest();return base64_encode(B)
		def N(user,password):return base64_encode('\x00%s\x00%s'%(user,password))
		H='PLAIN';I='CRAM-MD5';J='LOGIN';C.ehlo_or_helo_if_needed()
		if not C.has_extn(L):raise SMTPException('SMTP AUTH extension not supported by server.')
		O=C.esmtp_features[L].split();P=[I,H,J];E=None
		for K in P:
			if K in O:E=K;break
		if E==I:
			A=C.docmd(_A,I);B=A[0];D=A[1]
			if B==503:return B,D
			A=C.docmd(M(D,F,G));B=A[0];D=A[1]
		elif E==H:A=C.docmd(_A,H+' '+N(F,G));B=A[0];D=A[1]
		elif E==J:Q=base64_encode(F);R=base64_encode(G);A=C.check_codes(Q,R);B=A[0];D=A[1]
		elif E is None:raise SMTPException('No suitable authentication method found.')
		if B not in(235,503):raise SMTPAuthenticationError(B,D)
		return B,D
	def check_codes(D,encoded_username,encoded_password):
		E='LOGIN';B=D.docmd(_A,E);A=B[0];C=B[1]
		if A!=334:raise SMTPAuthenticationError(A,C)
		B=D.docmd(encoded_username);A=B[0];C=B[1]
		if A!=334:raise SMTPAuthenticationError(A,C)
		B=D.docmd(encoded_password);A=B[0];C=B[1]
		if A!=235:raise SMTPAuthenticationError(A,C)
		return A,C