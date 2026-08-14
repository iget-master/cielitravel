# Publica o site na AWS (S3 + CloudFront).
# Pré-requisitos: AWS CLI configurada (aws configure) e build feito (dist/).
#
# Uso:  .\infra\deploy.ps1               # stack padrão "cielitravel-site"
#       .\infra\deploy.ps1 -BucketName meu-bucket -StackName minha-stack
param(
    [string]$StackName = "cielitravel-site",
    [string]$BucketName = "cielitravel-site"
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

Write-Host "1/3 CloudFormation deploy ($StackName)..."
aws cloudformation deploy `
    --template-file "$root\infra\cloudformation.yml" `
    --stack-name $StackName `
    --parameter-overrides BucketName=$BucketName

$outputs = aws cloudformation describe-stacks --stack-name $StackName `
    --query "Stacks[0].Outputs" | ConvertFrom-Json
$bucket = ($outputs | Where-Object OutputKey -eq "BucketName").OutputValue
$distId = ($outputs | Where-Object OutputKey -eq "DistributionId").OutputValue
$url = ($outputs | Where-Object OutputKey -eq "SiteURL").OutputValue

Write-Host "2/3 Sync dist/ -> s3://$bucket ..."
aws s3 sync "$root\dist" "s3://$bucket" --delete

Write-Host "3/3 Invalidando cache do CloudFront ($distId)..."
aws cloudfront create-invalidation --distribution-id $distId --paths "/*" | Out-Null

Write-Host ""
Write-Host "Publicado: $url"
