functions = {
    # Windows --------
    'windows_dict': {
        'launch_bundle_names': None
    },
    'windows': """
# Launch Bundles
function ec2lm_launch_bundles([string]$CACHE_ID, [string]$SYNC_FLAG)
{{
    echo "EC2LM: Launch Bundles: Start"

    $EC2LM_IGNORE_CACHE = $false
    $EC2LM_ON_LAUNCH = $false
    $EC2LM_CACHE_FILE = "$EC2LM_FOLDER\ec2lm_cache_id.md5"
    $EC2LM_CACHE_FILE_PROCESSED = "$EC2LM_FOLDER\ec2lm_cache_id.md5.processed"
    if ( $CACHE_ID -eq "on_launch" ) {{
        $EC2LM_IGNORE_CACHE = $true
        $EC2LM_ON_LAUNCH = $true
        $SYNC_FLAG = "nosync"
    }}

    # Compare new EC2LM contents cache id with existing
    $OLD_CACHE_ID = "none"
    if ( Test-Path -Path $EC2LM_CACHE_FILE_PROCESSED -PathType Leaf ) {{
        $OLD_CACHE_ID = [IO.File]::ReadAllText($EC2LM_CACHE_FILE_PROCESSED)
    }}

    echo "EC2LM: -----------------------------------------------------"
    echo "EC2LM: Launch Bundles Start: $(Get-Date)"
    echo "EC2LM: CACHE_ID=$CACHE_ID"
    echo "EC2LM: OLD_CACHE_ID=$OLD_CACHE_ID"
    echo "EC2LM: EC2LM_IGNORE_CACHE=$EC2LM_IGNORE_CACHE"
    echo "EC2LM: EC2LM_ON_LAUNCH=$EC2LM_ON_LAUNCH"

    if ( $EC2LM_IGNORE_CACHE -eq $false ) {{
        if ( $CACHE_ID -eq $OLD_CACHE_ID ) {{
            echo "EC2LM: Cache Id unchanged. Skipping ec2lm_launch_bundles."
            echo "EC2LM: Launch Bundles End: $(Get-Date)"
            return
        }}
    }}

    # Synchronize latest bundle contents
    if ( $SYNC_FLAG -ne "nosync" ) {{
        echo "ec2lm_sync_folder"
    }} else {{
        echo "EC2LM: Launch Bundles: Folder sync skipped"
    }}

    # Run launch bundles
    #mkdir -p $EC2LM_FOLDER\LaunchBundles
    $LAUNCH_BUNDLE_FOLDER="${{EC2LM_FOLDER}}\LaunchBundles"
    cd $LAUNCH_BUNDLE_FOLDER

    echo "EC2LM: LaunchBundles: Loading"
    $LAUNCH_BUNDLE_NAMES = @({launch_bundle_names})
    foreach ( $BUNDLE_NAME in $LAUNCH_BUNDLE_NAMES)
    {{
        $BUNDLE_FOLDER = $BUNDLE_NAME
        $BUNDLE_PACKAGE = "${{LAUNCH_BUNDLE_FOLDER}}\${{BUNDLE_NAME}}.tgz"
        $BUNDLE_PACKAGE_CACHE_ID = "${{LAUNCH_BUNDLE_FOLDER}}\${{BUNDLE_NAME}}.cache_id"
        $BUNDLE_PACKAGE_CACHE_ID_PROCESSED = "${{BUNDLE_PACKAGE_CACHE_ID}}.processed"
        if ( -not(Test-Path -Path $BUNDLE_PACKAGE -PathType Leaf) ) {{
            echo "EC2LM: LaunchBundles: ${{BUNDLE_NAME}}: Skipping missing package: $BUNDLE_PACKAGE"
            continue
        }}
        # Check if this bundle has changed
        $NEW_BUNDLE_CACHE_ID = "cache id file is missing"

        echo "EC2LM: Reading Bundle package cache id from: ${{BUNDLE_PACKAGE_CACHE_ID}}"
        if ( Test-Path -Path $BUNDLE_PACKAGE_CACHE_ID -PathType Leaf ) {{
            $NEW_BUNDLE_CACHE_ID = [IO.File]::ReadAllText($BUNDLE_PACKAGE_CACHE_ID)
        }}
        if ( $EC2LM_IGNORE_CACHE -eq $false ) {{
            if ( Test-Path -Path $BUNDLE_PACKAGE_CACHE_ID_PROCESSED -PathType Leaf ) {{
                $OLD_BUNDLE_CACHE_ID=[IO.File]::ReadAllText($BUNDLE_PACKAGE_CACHE_ID_PROCESSED)
                if ( $NEW_BUNDLE_CACHE_ID -eq $OLD_BUNDLE_CACHE_ID ) {{
                    echo "EC2LM: LaunchBundles: Skipping cached bundle: ${{BUNDLE_NAME}}: ${{BUNDLE_PACKAGE}}: $NEW_BUNDLE_CACHE_ID == $OLD_BUNDLE_CACHE_ID"
                    continue
                }}
            }}
        }}
        echo "EC2LM: ==== $BUNDLE_PACKAGE"
        echo "EC2LM: SSHAccess: Begin"
        echo "EC2LM: LaunchBundles: ${{BUNDLE_NAME}}: Unpacking $BUNDLE_PACKAGE"

        tar xvfz $BUNDLE_PACKAGE
        echo "EC2LM: LaunchBundles: ${{BUNDLE_NAME}}: Launching bundle"
        cd $BUNDLE_FOLDER
        ./launch.ps1
        # Save the Bundle Cache ID after launch completion
        echo "EC2LM: LaunchBundles: ${{BUNDLE_NAME}}: Saving new cache id: $NEW_BUNDLE_CACHE_ID"
        cd ..
        Copy-Item -Path $BUNDLE_PACKAGE_CACHE_ID -Destination $BUNDLE_PACKAGE_CACHE_ID_PROCESSED
        echo "EC2LM: ========"
    }}
    echo "EC2LM: Storing new cache id: $CACHE_ID"
    if ( -not( Test-Path -Path $EC2LM_CACHE_FILE -PathType Leaf ) ) {{
        echo "$CACHE_ID" | Out-File -FilePath $EC2LM_CACHE_FILE
    }}
    Copy-Item -Path $EC2LM_CACHE_FILE -Destination $EC2LM_CACHE_FILE_PROCESSED
    echo "EC2LM: Launch Bundles End: $(Get-Date)"
    cd ..
}}
""",
    # Linux ----------
    'linux_dict': {
        'account_id': None,
        'paco_base_path': None,
        'tool_name': None,
        'netenv': None,
        'environment': None,
        'environment_ref': None,
        'ec2lm_bucket_name': None,
        'launch_bundle_names': None,
        'oldest_health_check_timeout': None,
        'install_wget': None,
        'install_package': None,
    },
    'linux': """INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
AVAIL_ZONE=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
REGION="$(echo \"$AVAIL_ZONE\" | sed 's/[a-z]$//')"
export AWS_DEFAULT_REGION=$REGION
EC2LM_AWS_ACCOUNT_ID="{account_id}"
EC2LM_STACK_NAME=$(aws ec2 describe-tags --region $REGION --filter "Name=resource-id,Values=$INSTANCE_ID" "Name=key,Values=aws:cloudformation:stack-name" --query 'Tags[0].Value' |tr -d '"')
EC2LM_FOLDER='{paco_base_path}/EC2Manager/'
EC2LM_{tool_name}_NETWORK_ENVIRONMENT="{netenv}"
EC2LM_{tool_name}_ENVIRONMENT="{environment}"
EC2LM_{tool_name}_ENVIRONMENT_REF={environment_ref}
CODEDEPLOY_BIN="/opt/codedeploy-agent/bin/codedeploy-agent"

# Escape a string for sed replacements
function sed_escape() {{
    RES="${{1//$'\\n'/\\\\n}}"
    RES="${{RES//./\\\\.}}"
    RES="${{RES//\\//\\\\/}}"
    RES="${{RES// /\\\\ }}"
    RES="${{RES//!/\\\\!}}"
    RES="${{RES//-/\\\\-}}"
    RES="${{RES//,/\\\\,}}"
    RES="${{RES//&/\\\\&}}"
    echo "${{RES}}"
}}

# Runs another function in a timeout loop.
# ec2lm_timeout <function> <timeout_secs>
#   <function> returns: 0 == success
#                       1 == keep waiting
#                     > 1 == error code and abort
#
# ec2lm_timeout returns: 0 == success
#                        1 == timed out
#                      > 1 == error
function ec2lm_timeout() {{
    TIMEOUT_SECS=$1
    shift
    FUNCTION=$1
    shift

    COUNT=0
    while :
    do
        OUTPUT=$($FUNCTION $@)
        RES=$?
        if [ $RES -eq 0 ] ; then
            echo $OUTPUT
            return $RES
        fi
        if [ $RES -gt 1 ] ; then
            echo "EC2LM: ec2lm_timeout: Function '$FUNCTION' returned an error: $RES: $OUTPUT"
            return $RES
        fi
        if [ $COUNT -eq $TIMEOUT_SECS ] ; then
            echo "EC2LM: ec2lm_timeout: Function '$FUNCTION' timed out after $TIMEOUT_SECS seconds"
            return 1
        fi
        COUNT=$(($COUNT + 1))
        sleep 1
    done

}}

# Sync EC2LM Folder
function ec2lm_sync_folder() {{
    echo "EC2LM: Folder: Sync Begin: aws s3 cp --recursive --region=$REGION s3://{ec2lm_bucket_name} $EC2LM_FOLDER"
    aws s3 cp --recursive --region=$REGION s3://{ec2lm_bucket_name} $EC2LM_FOLDER
    echo "EC2LM: Folder: Sync End"
}}

# Create a symlink
function ec2lm_symlink() {{
    TO_FOLDER=$1
    FROM_FOLDER=$2

    if [ -L "$FROM_FOLDER" -o -f "$FROM_FOLDER" ] ; then
        rm -f $FROM_FOLDER
    elif [ -d "$FROM_FOLDER" ] ; then
        rm -rf $FROM_FOLDER
    fi
    echo ln -s $TO_FOLDER $FROM_FOLDER
    ln -s $TO_FOLDER $FROM_FOLDER
}}

# Launch Bundles
function ec2lm_launch_bundles() {{
    CACHE_ID=$1
    SYNC_FLAG=$2

    export EC2LM_IGNORE_CACHE="false"
    export EC2LM_ON_LAUNCH="false"
    EC2LM_CACHE_FILE=$EC2LM_FOLDER/ec2lm_cache_id.md5
    EC2LM_CACHE_FILE_PROCESSED=$EC2LM_FOLDER/ec2lm_cache_id.md5.processed
    if [ "$CACHE_ID" == "on_launch" ] ; then
        export EC2LM_IGNORE_CACHE="true"
        export EC2LM_ON_LAUNCH="true"
        SYNC_FLAG="nosync"
    fi

    # Compare new EC2LM contents cache id with existing
    OLD_CACHE_ID="none"
    if [ -e "$EC2LM_CACHE_FILE_PROCESSED" ] ; then
        OLD_CACHE_ID=$(<$EC2LM_CACHE_FILE_PROCESSED)
    fi

    echo "EC2LM: -----------------------------------------------------"
    echo "EC2LM: Launch Bundles Start: $(date)"
    echo "EC2LM: CACHE_ID=$CACHE_ID"
    echo "EC2LM: OLD_CACHE_ID=$OLD_CACHE_ID"
    echo "EC2LM: EC2LM_IGNORE_CACHE=$EC2LM_IGNORE_CACHE"
    echo "EC2LM: EC2LM_ON_LAUNCH=$EC2LM_ON_LAUNCH"

    if [ "$EC2LM_IGNORE_CACHE" == "false" ] ; then
        if [ "$CACHE_ID" == "$OLD_CACHE_ID" ] ; then
            echo "EC2LM: Cache Id unchanged. Skipping ec2lm_launch_bundles."
            echo "EC2LM: Launch Bundles End: $(date)"
            return
        fi
    fi

    # EC2LM Lock file
    EC2LM_LOCK_FILE_TIMEOUT_SECS=60
    EC2LM_LOCK_FOLDER=/var/lock/paco/
    mkdir -p $EC2LM_LOCK_FOLDER
    EC2LM_LOCK_FILE=$EC2LM_LOCK_FOLDER/ec2lm.lock
    if [ ! -f $EC2LM_LOCK_FILE ]; then
        :>$EC2LM_LOCK_FILE
    fi
    exec 100>$EC2LM_LOCK_FILE
    echo "EC2LM: LaunchBundles: Obtaining lock."
    flock -n 100
    RET=$?
    if [ $RET -ne 0 ] ; then
        echo "[LOCK] Another EC2LM is holding a lock. Waiting for $EC2LM_LOCK_FILE_TIMEOUT_SECS seconds"
        lsof $EC2LM_LOCK_FILE
        echo flock -w --timeout $EC2LM_LOCK_FILE_TIMEOUT_SECS 100
        flock -w --timeout $EC2LM_LOCK_FILE_TIMEOUT_SECS 100
        RET=$?
        if [ $RET -ne 0 ] ; then
            echo “[ERROR] EC2LM LaunchBundles: Unable to obtain EC2LM lock: $RET”
            echo "EC2LM: Launch Bundles End: $(date)"
            return 1
        fi
    fi

    # Synchronize latest bundle contents
    if [ "$SYNC_FLAG" != "nosync" ] ; then
        ec2lm_sync_folder
    else
        echo "EC2LM: Launch Bundles: Folder sync skipped"
    fi

    # Run launch bundles
    mkdir -p $EC2LM_FOLDER/LaunchBundles/
    cd $EC2LM_FOLDER/LaunchBundles/

    echo "EC2LM: LaunchBundles: Loading"
    for BUNDLE_NAME in {launch_bundle_names}
    do
        BUNDLE_FOLDER=$BUNDLE_NAME
        BUNDLE_PACKAGE=$BUNDLE_NAME".tgz"
        BUNDLE_PACKAGE_CACHE_ID=$BUNDLE_NAME".cache_id"
        BUNDLE_PACKAGE_CACHE_ID_PROCESSED=$BUNDLE_PACKAGE_CACHE_ID".processed"
        if [ ! -f "$BUNDLE_PACKAGE" ] ; then
            echo "EC2LM: LaunchBundles: $BUNDLE_NAME: Skipping missing package: $BUNDLE_PACKAGE"
            continue
        fi
        # Check if this bundle has changed
        NEW_BUNDLE_CACHE_ID="cache id file is missing"

        if [ -e $BUNDLE_PACKAGE_CACHE_ID ] ; then
            NEW_BUNDLE_CACHE_ID=$(cat $BUNDLE_PACKAGE_CACHE_ID)
        fi
        if [ "$EC2LM_IGNORE_CACHE" == "false" ] ; then
            if [ -e $BUNDLE_PACKAGE_CACHE_ID_PROCESSED ] ; then
                OLD_BUNDLE_CACHE_ID=$(cat $BUNDLE_PACKAGE_CACHE_ID_PROCESSED)
                if [ "$NEW_BUNDLE_CACHE_ID" == "$OLD_BUNDLE_CACHE_ID" ] ; then
                    echo "EC2LM: LaunchBundles: Skipping cached bundle: $BUNDLE_NAME: $BUNDLE_PACKAGE: $NEW_BUNDLE_CACHE_ID == $OLD_BUNDLE_CACHE_ID"
                    continue
                fi
            fi
        fi
        echo "EC2LM: ==== $BUNDLE_PACKAGE"
        echo "EC2LM: SSHAccess: Begin"
        echo "EC2LM: LaunchBundles: $BUNDLE_NAME: Unpacking $BUNDLE_PACKAGE"
        tar xvfz $BUNDLE_PACKAGE
        chown -R root.root $BUNDLE_FOLDER
        echo "EC2LM: LaunchBundles: $BUNDLE_NAME: Launching bundle"
        cd $BUNDLE_FOLDER
        chmod u+x ./launch.sh
        ./launch.sh
        # Save the Bundle Cache ID after launch completion
        echo "EC2LM: LaunchBundles: $BUNDLE_NAME: Saving new cache id: $NEW_BUNDLE_CACHE_ID"
        cd ..
        cp -f $BUNDLE_PACKAGE_CACHE_ID $BUNDLE_PACKAGE_CACHE_ID_PROCESSED
        echo "EC2LM: ========"
    done
    echo "EC2LM: Storing new cache id: $CACHE_ID"
    if [ ! -e "$EC2LM_CACHE_FILE" ] ; then
        echo "$CACHE_ID" >$EC2LM_CACHE_FILE
    fi
    cp $EC2LM_CACHE_FILE $EC2LM_CACHE_FILE_PROCESSED
    echo "EC2LM: Launch Bundles: End"
}}

# Instance Tags
function ec2lm_instance_tag_value() {{
    TAG_NAME="$1"
    aws ec2 describe-tags --region $REGION --filter "Name=resource-id,Values=$INSTANCE_ID" "Name=key,Values=$TAG_NAME" --query 'Tags[0].Value' |tr -d '"'
}}

# Is a CodeDeploy deployment in place?
function ec2lm_wait_for_codedeploy() {{
    if [ ! -e $CODEDEPLOY_BIN ] ; then
        return 0
    fi
    set +e
    # 15 minutes
    SLEEP_SECS=10
    TIMEOUT_MINS=15
    TIMEOUT_COUNT=$(($((60*$TIMEOUT_MINS))/$SLEEP_SECS))
    T_COUNT=0
    DEPLOYMENT_INPROGRESS=False
    while :
    do
        OUTPUT=$($CODEDEPLOY_BIN stop 2>/dev/null)
        if [ $? -eq 0 ] ; then
            break
        fi
        echo "EC2LM: CodeDeploy: A deployment is in progress, waiting for deployment to complete."
        DEPLOYMENT_INPROGRESS=True
        sleep $SLEEP_SECS
        T_COUNT=$(($T_COUNT+1))
        if [ $T_COUNT -eq $TIMEOUT_COUNT ] ; then
            echo "EC2LM: CodeDeploy: ERROR: Timeout after $TIMEOUT_MINS minutes waiting for deployment to complete."
            exit 1
        fi
    done
    if [ "$DEPLOYMENT_INPROGRESS" == "True" ]; then
        echo "EC2LM: CodeDeploy: Deployment finished."
    fi
    echo "EC2LM: Starting CodeDeploy Agent"
    $CODEDEPLOY_BIN start 2>/dev/null
    set -e
}}

# Signal the ASG resource
function ec2lm_signal_asg_resource() {{
    STATUS=$1
    if [ "$STATUS" != "SUCCESS" -a "$STATUS" != "FAILURE" ] ; then
        echo "EC2LM: Signal ASG Resource: Error: Invalid status: $STATUS: Valid values: SUCCESS | FAILURE"
        return 1
    fi
    STACK_STATUS=$(aws cloudformation describe-stacks --stack $EC2LM_STACK_NAME --region $REGION --query "Stacks[0].StackStatus" | tr -d '"')
    echo "EC2LM: Signal ASG Resource: Stack status: $STACK_STATUS"
    if [[ "$STACK_STATUS" == *"PROGRESS" ]]; then
        # ASG Rolling Update
        ASG_LOGICAL_ID=$(ec2lm_instance_tag_value 'aws:cloudformation:logical-id')
        # Wait for deployments if they are ongoing
        ec2lm_wait_for_codedeploy
        # Sleep to allow ALB healthcheck to succeed otherwise older instances will begin to shutdown
        echo "EC2LM: Signal ASG Resource: Sleeping for {oldest_health_check_timeout} seconds to allow target healthcheck to succeed."
        sleep {oldest_health_check_timeout}
        echo "EC2LM: Signal ASG Resource: Signaling ASG Resource: $EC2LM_STACK_NAME: $ASG_LOGICAL_ID: $INSTANCE_ID: $STATUS"
        aws cloudformation signal-resource --region $REGION --stack $EC2LM_STACK_NAME --logical-resource-id $ASG_LOGICAL_ID --unique-id $INSTANCE_ID --status $STATUS
    else
        echo "EC2LM: Resource Signaling: Not a rolling update: skipping"
    fi
}}

# Swap
function swap_on() {{
    SWAP_SIZE_GB=$1
    if [ -e /swapfile ] ; then
        CUR_SWAP_FILE_SIZE=$(stat -c '%s' /swapfile)
        if [ $CUR_SWAP_FILE_SIZE -eq $(($SWAP_SIZE_GB*1073741824)) ] ; then
            set +e
            OUTPUT=$(swapon /swapfile 2>&1)
            RES=$?
            if [ $RES -eq 0 ] ; then
                echo "EC2LM: Swap: Enabling existing ${{SWAP_SIZE_GB}}GB Swapfile: /swapfile"
            else
                if [[ $OUTPUT == *"Device or resource busy"* ]] ; then
                    echo  "EC2LM: Swap: $OUTPUT"
                elif [[ $RES -ne 0 ]] ; then
                    echo "EC2LM: Swap: Error: $OUTPUT"
                    return 255
                fi
            fi
            set -e
        fi
    fi
    if [ "$(swapon -s|grep -v Filename|wc -c)" == "0" ]; then
        echo "EC2LM: Swap: Enabling a ${{SWAP_SIZE_GB}}GB Swapfile: /swapfile"
        dd if=/dev/zero of=/swapfile bs=1024 count=$(($SWAP_SIZE_GB*1024))k
        chmod 0600 /swapfile
        mkswap /swapfile
        swapon /swapfile
    else
        echo "EC2LM: Swap: Swap already enabled"
    fi
    swapon -s
    free
    echo "EC2LM: Swap: Done"
}}

# Install Wget
function ec2lm_install_wget() {{
    CLIENT_PATH=$(which wget)
    if [ $? -eq 1 ] ; then
        {install_wget}
    fi
}}

# Install Wget
function ec2lm_install_package() {{
    INSTALL_CMD="{install_package} $1"
    echo "EC2LM: Install Package: $1"
    OUTPUT=$($INSTALL_CMD 2>&1)
    RET=$?
    if [ $RET -ne 0 ] ; then
        echo "EC2LM: Install Package: $1: Returned an Error:"
        echo $OUTPUT
    fi
}}

# Set EC2 DNS
function ec2lm_set_dns() {{
    INSTANCE_HOSTNAME="$(curl http://169.254.169.254/latest/meta-data/hostname 2>/dev/null)"
    RECORD_SET_FILE=/tmp/internal_record_set.json
    DOMAIN=$1
    HOSTED_ZONE_ID=$2
    cat << EOF >$RECORD_SET_FILE
{{
"Comment": "API Server",
"Changes": [ {{
    "Action": "UPSERT",
    "ResourceRecordSet": {{
        "Name": "$DOMAIN",
        "Type": "CNAME",
        "TTL": 60,
        "ResourceRecords": [ {{
            "Value": "$INSTANCE_HOSTNAME"
        }} ]
    }}
}} ]
}}
EOF
    OUTPUT=$(aws route53 change-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --change-batch file://$RECORD_SET_FILE 2>&1)
    RET=$?
    if [ $RET -ne 0 ] ; then
        echo "EC2LM: DNS: ERROR: Unable to set DNS:"
        echo $OUTPUT
        return 0
    fi
}}

# Set EC2 DNS
function ec2lm_set_dns_cname() {{
    RECORD_SET_FILE=/tmp/internal_record_set.json
    DOMAIN=$1
    CNAME_RECORD="$2"
    HOSTED_ZONE_ID=$2
    cat << EOF >$RECORD_SET_FILE
{{
"Comment": "API Server",
"Changes": [ {{
    "Action": "UPSERT",
    "ResourceRecordSet": {{
        "Name": "$DOMAIN",
        "Type": "CNAME",
        "TTL": 60,
        "ResourceRecords": [ {{
            "Value": "$CNAME_RECORD"
        }} ]
    }}
}} ]
}}
EOF
    aws route53 change-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --change-batch file://$RECORD_SET_FILE
}}
"""
}

secrets = {
    'windows': "",
    'linux': """
function ec2lm_get_secret() {
    aws secretsmanager get-secret-value --secret-id "$1" --query SecretString --region $REGION --output text
}

function ec2lm_get_secret_from_json() {
    SECRET_ID=$1
    SECRET_KEY=$2

    SECRET_JSON=$(ec2lm_get_secret $SECRET_ID)
    echo $SECRET_JSON | jq -r ".${SECRET_KEY}"
}

# ec2lm_replace_secret_in_file <secret id> <file> <replace pattern>
function ec2lm_replace_secret_in_file() {
    SECRET_ID=$1
    SED_PATTERN=$2
    REPLACE_FILE=$3
    SECRET=$(ec2lm_get_secret $SECRET_ID)

    sed -i -e "s/$SED_PATTERN/$SECRET/" $REPLACE_FILE
}

# ec2lm_replace_secret_in_file_from_json <secret id> <replace pattern> <file> <secret name>
function ec2lm_replace_secret_in_file_from_json() {
    SECRET_ID=$1
    SED_PATTERN=$2
    REPLACE_FILE=$3
    SECRET_KEY=$4
    SECRET=$(ec2lm_get_secret_from_json $SECRET_ID $SECRET_KEY)
    sed -i -e "s/$SED_PATTERN/$(sed_escape $SECRET)/" $REPLACE_FILE
}
"""
}

async_run = {
    'linux': """

# ------------------------------------
# Asynchronous Run Commands
declare -a EC2LM_ASYNC_RUN_PID
declare -a EC2LM_ASYNC_RUN_COMMAND
declare -a EC2LM_ASYNC_RUN_LOG
EC2LM_ASYNC_RUN_IDX=0

function ec2lm_async_run() {
    DESCRIPTION=$1
    COMMAND=$2
    if [ "${DESCRIPTION}" == "" ] ; then
            DESCRIPTION="${COMMAND}"
    fi
    echo "async run: ${DESCRIPTION}"
    EC2LM_ASYNC_RUN_LOG[$EC2LM_ASYNC_RUN_IDX]=$(mktemp)
    #echo -n "Async Run: command = '${COMMAND}'"
    eval $COMMAND >${EC2LM_ASYNC_RUN_LOG[$EC2LM_ASYNC_RUN_IDX]} 2>&1 &
    EC2LM_ASYNC_RUN_PID[$EC2LM_ASYNC_RUN_IDX]=$!
    EC2LM_ASYNC_RUN_COMMAND[$EC2LM_ASYNC_RUN_IDX]=$COMMAND
    #echo ": pid = ${EC2LM_ASYNC_RUN_PID[$EC2LM_ASYNC_RUN_IDX]}"

    EC2LM_ASYNC_RUN_IDX=$(($EC2LM_ASYNC_RUN_IDX+1))
}

function ec2lm_async_run_wait() {
    echo "async wait: start"
    while :
    do
        WAIT_DONE=true
        for ((IDX=0;$IDX<$EC2LM_ASYNC_RUN_IDX;IDX++))
        do
            if [ ${EC2LM_ASYNC_RUN_PID[$IDX]} -eq 0 ] ; then
                # PID changes to 0 when the command has finished
                continue
            fi
            kill -0 ${EC2LM_ASYNC_RUN_PID[$IDX]} >/dev/null 2>&1
            RET=$?
            if [ $RET -ne 0 ] ; then
                # Get exit code
                wait ${EC2LM_ASYNC_RUN_PID[$IDX]}
                COMMAND_RET=$?
                if [ $COMMAND_RET -ne 0 ] ; then
                    echo "async wait: error: exit code = ${RET}: ${EC2LM_ASYNC_RUN_COMMAND[$IDX]}"
                    echo "---------------------------------------"
                    cat ${EC2LM_ASYNC_RUN_LOG[$IDX]}
                    echo "---------------------------------------"
                else
                    echo "async wait: success: ${EC2LM_ASYNC_RUN_COMMAND[$IDX]}"
                fi
                if [ $COMMAND_RET -ne 0 ] ; then
                    exit 255
                fi
                EC2LM_ASYNC_RUN_PID[$IDX]=0
                continue
            fi
            WAIT_DONE="false"
        done
        if [ "$WAIT_DONE" == "true" ] ; then
            break
        fi
        sleep 1
    done
    echo "async wait: done"
    return 0
}

"""
}

# User Data Script -----------------------------------------------------------------------------
user_data_script = {
    # -- Windows
    'windows_dict': {
        'ec2lm_bucket_name': None,
        'region': None,
        'paco_base_path': None,
        'pre_script': None,
        'install_aws_cli': None
    },
    'windows': """<powershell>
echo "Paco EC2LM: Powershell Script"

{pre_script}
{install_aws_cli}

$env:Path += ";C:\\Program Files\\Amazon\\AWSCLIV2\\"

$EC2LM_FOLDER = '{paco_base_path}\\EC2Manager'
$EC2LM_FUNCTIONS = "ec2lm_functions.ps1"
echo "Creating folder: $EC2LM_FOLDER"
New-Item -ItemType Directory -Force -Path $EC2LM_FOLDER

$completed = $false
$retrycount = 60
$secondsDelay = 1
$cmd = "aws s3 cp --recursive --region={region} s3://{ec2lm_bucket_name} $EC2LM_FOLDER"

echo "Downloading EC2 Bundles"
while (-not $completed) {{
    Try{{
        Invoke-Expression $cmd
        if ($lastexitcode) {{throw "Error running command"}}

        Write-Verbose ("Command [{{0}}] succeeded." -f $cmd)
        $completed = $true
    }}Catch{{
        if ($retrycount -ge $retries) {{
            Write-Host ("Command [{{0}}] failed the maximum number of {{1}} times." -f $cmd, $retrycount)
            throw
        }} else {{
            Write-Host ("Command [{{0}}] failed. Retrying in {{1}} seconds." -f $cmd, $secondsDelay)
            Start-Sleep $secondsDelay
            $retrycount++
        }}
    }}
}}

. $EC2LM_FOLDER/$EC2LM_FUNCTIONS

# Run every Paco EC2LM launch bundle on launch

echo "Creating Logs folder: $EC2LM_FOLDER\logs"
New-Item -ItemType Directory -Force -Path $EC2LM_FOLDER\logs

ec2lm_launch_bundles
</powershell>
""",
    # -- Linux --------------------------------------------------------------------------------
    'linux_dict': {
        'ec2lm_bucket_name': None,
        'region': None,
        'paco_base_path': None,
        'pre_script': None,
        'install_aws_cli': None,
        'update_packages': None
    },
    'linux': """#!/bin/bash
echo "Paco EC2LM: Script: $0"

# Runs pip
function ec2lm_pip() {{
    for PIP_CMD in pip3 pip2 pip
    do
        which $PIP_CMD >/dev/null 2>&1
        if [ $? -eq 0 ] ; then
            $PIP_CMD $@
            return
        fi
    done
}}

{pre_script}
{update_packages}
{install_aws_cli}

EC2LM_FOLDER='{paco_base_path}/EC2Manager/'
EC2LM_FUNCTIONS=ec2lm_functions.bash
mkdir -p $EC2LM_FOLDER/
set +e
TIMEOUT=60
COUNT=0
while :
do
    aws s3 cp --recursive --region={region} s3://{ec2lm_bucket_name} $EC2LM_FOLDER
    RET=$?
    if [ $RET -ne 0 ] ; then
        if [ $COUNT -eq $TIMEOUT ]; then
            "EC2LM: ERROR: Timeout while waiting for EC2LM bucket sync."
            exit $RET
        fi
        COUNT=$(($COUNT+1))
        echo "EC2LM: ERROR: Unable to download EC2LM bucket: Missing IAM role or race condition?"
        sleep 1
        continue
    fi
    break
done
set -e

. $EC2LM_FOLDER/$EC2LM_FUNCTIONS

# Run every Paco EC2LM launch bundle on launch
mkdir -p /var/log/paco
ec2lm_launch_bundles on_launch

"""
}