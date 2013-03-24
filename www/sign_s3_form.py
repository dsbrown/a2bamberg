import base64
import hmac, hashlib

policy = base64.b64encode(open('s3_upload_policy.json').read())

AWS_SECRET_ACCESS_KEY = raw_input('Enter your AWS Secret Access Key (http://goo.gl/MCoeg): ')

signature = base64.b64encode(hmac.new( AWS_SECRET_ACCESS_KEY, policy, hashlib.sha1).digest())

print('\nPolicy:\n==================\n{}\n'.format(policy))

print('Signature:\n==================\n{}\n==================\n'.format(signature))