# Build Jpylyzer Windows packages 

function Get-Jpylyzer-Version {
    python cli.py --version
}

function buildAndPackage {

}

$SCRIPT_DIR=$PSSCriptRoot
echo $SCRIPT_DIR

Get-Jpylyzer-Version
