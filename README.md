# JB::EMR::StepConcurrencyLevel

This resource type is used to set the StepConcurrencyLevel attribute in
an Amazon Elastic Map Reduce (EMR) cluster. By default the value is set to
1 when a cluster is created and the current AWS::EMR::Cluster does not
have an option to set this attribute.

When creating the resource the ID of an existing cluster needs to be
passed in along with the new StepConcurrencyLevel value between the
minimum of 1 to the maximum of 256.

When the CloudFormation resource is deleted the StepConcurrencyLevel is set back to the default value of 1.

## Usage

View the [README](docs/README.md) for information about using the resource type.

Deployment into the account is done via the [CloudFormation CLI](https://docs.aws.amazon.com/cloudformation-cli/latest/userguide/what-is-cloudformation-cli.html) command `cfn submit`. See the page on [Registering Resource Providers](https://docs.aws.amazon.com/cloudformation-cli/latest/userguide/resource-type-register.html) for more details.

## Testing

When running `cfn test` to test the resource you will need a working EMR
cluster in your AWS account. With the cluster running update the .json
files in the inputs folder with the ClusterID of your EMR cluster.
