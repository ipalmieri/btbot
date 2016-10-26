
basedir=$(dirname "$0")
logdir=$basedir/logs

if ! [ -d $logdir ]; then
    echo "Creating log folder $logdir"
    mkdir $logdir
fi


cat > $basedir/settings.py << EOF
BTDATA_PARAMS = {
    'drivername': 'postgres',
    'host': 'SERVER',
    'port': 'PORT',
    'username': 'USER',
    'password': 'PASS',
    'database': 'DATABASE'
}

MBTC_PARAMS = {
    'tapi_id' : 'TAPID',
    'tapi_secret' : 'TAPISEC'
}
EOF


