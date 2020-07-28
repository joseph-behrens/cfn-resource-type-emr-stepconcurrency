# JB::EMR::StepConcurrencyLevel

Updates the Step Concurrency Level of an existing EMR cluster.

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "Type" : "JB::EMR::StepConcurrencyLevel",
    "Properties" : {
        "<a href="#clusterid" title="ClusterId">ClusterId</a>" : <i>String</i>,
        "<a href="#stepconcurrencylevel" title="StepConcurrencyLevel">StepConcurrencyLevel</a>" : <i>Integer</i>
    }
}
</pre>

### YAML

<pre>
Type: JB::EMR::StepConcurrencyLevel
Properties:
    <a href="#clusterid" title="ClusterId">ClusterId</a>: <i>String</i>
    <a href="#stepconcurrencylevel" title="StepConcurrencyLevel">StepConcurrencyLevel</a>: <i>Integer</i>
</pre>

## Properties

#### ClusterId

The unique ID of the EMR cluster to set the step concurrency level

_Required_: Yes

_Type_: String

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### StepConcurrencyLevel

Level to set the step concurrency from 1 (default level) to 256.

_Required_: Yes

_Type_: Integer

_Pattern_: <code>^[1-9]$|^[1-9][0-9]$|^1[0-9][0-9]$|^2[0-4][0-9]$|^25[0-6]$</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

## Return Values

### Ref

When you pass the logical ID of this resource to the intrinsic `Ref` function, Ref returns the UID.

### Fn::GetAtt

The `Fn::GetAtt` intrinsic function returns a value for a specified attribute of this type. The following are the available attributes and sample return values.

For more information about using the `Fn::GetAtt` intrinsic function, see [Fn::GetAtt](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).

#### UID

A unique ID for the resource

