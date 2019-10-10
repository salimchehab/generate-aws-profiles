import boto3
from jinja2 import Environment, FileSystemLoader
import os
import yaml

generated_aws_config_file_name = "config"
generated_aws_extend_switch_role_file_name = "extend-switch-role-firefox"

aws_config_data = yaml.safe_load(open("./aws_profiles.yml"))
aws_config_env = Environment(loader=FileSystemLoader("./templates/"), trim_blocks=True, lstrip_blocks=True)

aws_config_template = aws_config_env.get_template("config.j2")
aws_extend_switch_role_template = aws_config_env.get_template("aws_extend_switch_roles_firefox.j2")

if os.path.isfile(generated_aws_config_file_name) or os.path.isfile(generated_aws_extend_switch_role_file_name):
    print(
        f"One of the following files already exists: {generated_aws_config_file_name}, or {generated_aws_extend_switch_role_file_name}.")
    generate_files = input(
        "Would you like to continue? (Note that this will overwrite the existing config files)? (Y/n):")
    if generate_files != "Y":
        print("Exiting without generating any files!")
        exit(1)

with open(f"{generated_aws_config_file_name}", mode="w") as config_writer:
    config_writer.write(aws_config_template.render(aws_config_data))

with open(f"{generated_aws_extend_switch_role_file_name}", mode="w") as extend_switch_role_writer:
    extend_switch_role_writer.write(aws_extend_switch_role_template.render(aws_config_data))

print(
    f"Successfully generated files: {generated_aws_config_file_name}, and {generated_aws_extend_switch_role_file_name}.")
do_mfa = input(
    "Would you like to authenticate with your MFA device (this will append the default profile and aws_session_token to the config file)? (Y/n):")

if do_mfa == "Y":
    session = boto3.session.Session()
    sts_client = session.client('sts')

    caller_identity = sts_client.get_caller_identity()
    account = caller_identity.get("Account")
    user = caller_identity.get("Arn").split("/")[1]

    mfa_serial_number = f"arn:aws:iam::{account}:mfa/{user}"
    mfa_token_code = input("Input MFA Token Code:")
    mfa_token_code = str(mfa_token_code)

    sts_credentials = sts_client.get_session_token(DurationSeconds=43200, SerialNumber=mfa_serial_number,
                                                   TokenCode=mfa_token_code)
    credentials = sts_credentials["Credentials"]

    with open(f"{generated_aws_config_file_name}", mode="a") as config_writer:
        config_writer.write("\n")
        config_writer.write("### MFA Authenticated\n")
        config_writer.write("[default]\n")
        config_writer.write("aws_session_token = " + credentials['SessionToken'] + "\n")
        config_writer.write("aws_access_key_id = " + credentials['AccessKeyId'] + "\n")
        config_writer.write("aws_secret_access_key = " + credentials['SecretAccessKey'] + "\n")
        config_writer.write("region = " + aws_config_data.get("mfa_region") + "\n")
        config_writer.write("output = json\n")
        config_writer.write("cli_history = enabled\n")

    print(
        f"Successfully added your aws_session_token to {generated_aws_config_file_name} (valid for the next 12 hours).")
else:
    print("See you later then!")

exit(0)
