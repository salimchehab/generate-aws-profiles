### Generate AWS Profiles in `~/.aws/config`  

[AWS profiles](https://docs.aws.amazon.com/sdk-for-php/v3/developer-guide/guide_credentials_profiles.html) are useful when it comes to multiple accounts and roles.

I found myself once working with more than 18 AWS accounts. It would be very hard to manage them all without having a central place where I can place the accounts and the roles that I can assume in each account. Additionally, [MFA](https://aws.amazon.com/iam/features/mfa/) was enabled on all of them so I needed a session token every time I wanted to use the CLI/API. 

This python script generates, based on the yaml template file, the following files:

- AWS `config` (usually located next to the `credentials` file in the `~/.aws` directory).
- `extend-switch-role`(used by the Firefox add-on [AWS Extend Switch Roles](https://addons.mozilla.org/en-US/firefox/addon/aws-extend-switch-roles3/).

In addition, it takes in the AWS MFA token code and appends it to the end of the generated AWS `config` file so that the user can work with the profiles when authenticated. The duration is currently set to the maximum possible value of 43200 seconds (12 hours). 

It uses the `Jinja2` templates located in the templates folder:

This assumes that you have your AWS `credentials` file already configured with your `aws_access_key_id` and `aws_secret_access_key`.

- `config.j2`: the AWS account profiles will be generated and from the list of dictionaries provided in `aws_accounts` in the yaml file. This can be edited according to your accounts and roles.

I usually have this script located in `~/.aws/` and run it from inside that directory to generate the config files directly in there.

Example run:

```text
$ python3.6 /Users/salimchehab/.aws/generate_aws_config.py
One of the following files already exists: config, or extend-switch-role-firefox.
Would you like to continue? (Note that this will overwrite the existing config files)? (Y/n):Y
Successfully generated files: config, and extend-switch-role-firefox.
Would you like to authenticate with your MFA device (this will append the default profile and aws_session_token to the config file)? (Y/n):Y
Input MFA Token Code:044416
Successfully added your aws_session_token to config (valid for the next 12 hours).
```

Output file examples can be found in the [sample output folder](./sample_output).

Afterwards we can use the aws cli commands with our favorite profile:
    
    $ aws ec2 describe-regions --profile something-dev