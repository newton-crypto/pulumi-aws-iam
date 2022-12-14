# Pulumi-aws-iam-poc (Python)

This repo ports over the retinal-scanner code and packages it to be uploaded to the pulumi registry to be used in a 'write once and use anywhere' fashion. 

### Background
This repository is based off of the [guide for authoring and publishing a Pulumi Package](https://www.pulumi.com/docs/guides/pulumi-packages/how-to-author).

Learn about the concepts behind [Pulumi Packages](https://www.pulumi.com/docs/guides/pulumi-packages/#pulumi-packages) and, more specifically, [Pulumi Components](https://www.pulumi.com/docs/intro/concepts/resources/components/)

## IAM Component Provider

Pulumi component providers make
[component resources](https://www.pulumi.com/docs/intro/concepts/resources/#components)
available to Pulumi code in all supported programming languages.

The iam.py defines functions to easily create AWS Roles and Policies

The important pieces include:

- [schema.json](schema.json) declaring the `Role`, `Policy`, and `PolicyStatement`

- [aws_iam](provider/cmd/pulumi-resource-aws-iam/aws_iam/provider.py) package
  implementing `Role` and `Policy` using typical Pulumi Python code

From here, the build generates:

- SDKs for Python, Go, .NET, and Node (under `sdk/`)

- `pulumi-resource-aws-iam` Pulumi plugin (under `bin/`)

Users can deploy `Role` and `Policy` instances in their language of choice,
as seen in the [TypeScript example](examples/simple/index.ts). Only
two things are needed to run `pulumi up`:

- the code needs to reference the `aws-iam` SDK package

- `pulumi-resource-aws-iam` needs to be on `PATH` for `pulumi` to find it


## Prerequisites

- Pulumi CLI
- Python 3.6+
- Node.js
- Yarn
- Go 1.17
- Node.js (to build the Node SDK)
- .NET Code SDK (to build the .NET SDK)


## Build and Test

```bash

# Regenerate SDKs
make generate

# Build and install the provider and SDKs
make build
make install

# Ensure the pulumi-provider-xyz script is on PATH (for testing)
$ export PATH=$PATH:$PWD/bin

# Test Node.js SDK
$ cd examples/simple
$ yarn install
$ yarn link @pulumi/xyz
$ pulumi stack init test
$ pulumi config set aws:region us-east-1
$ pulumi up

```

## Naming

The `aws-iam` plugin must be packaged as a `pulumi-resource-aws-iam` script or
binary (in the format `pulumi-resource-<provider>`).

While the plugin must follow this naming convention, the SDK package
naming can be custom.

## Packaging

The `aws-iam` plugin can be packaged as a tarball for distribution:

```bash
$ make dist

$ ls dist/
pulumi-resource-xyz-v0.0.1-darwin-amd64.tar.gz
pulumi-resource-xyz-v0.0.1-windows-amd64.tar.gz
pulumi-resource-xyz-v0.0.1-linux-amd64.tar.gz
```

Users can install the plugin with:

```bash
pulumi plugin install resource xyz 0.0.1 --file dist/pulumi-resource-xyz-v0.0.1-darwin-amd64.tar.gz
```

The tarball only includes the `aws-iam` sources. During the
installation phase, `pulumi` will use the user's system Python command
to rebuild a virtual environment and restore dependencies (such as
Pulumi SDK).

## Configuring CI and releases

1. Follow the instructions laid out in the [deployment templates](./deployment-templates/README-DEPLOYMENT.md).

## Changes and Findings

The reason behind authoring the pulumi package and porting over code from retinal scanner was to have all of the black-mesa submodules upload onto the pulumi registry. That way, all the modules can be imported and used across languages. The specific use case was to have all our modules uploaded to registry so that our Lambda boilerplate can import and access them even though the modules were originally written in Python.

The work done in the repo so far include some replacing the example StaticPage to our IAM Role and Policy resources everywhere it is mentioned, a new schema.json to reflect retinal-scanner, bringing over the code from retinal-scanner, and restructing it to match the example's format.

Issues that were encountered while authoring include :
- Overloading the provider.py's construct(). The basic example does not cover what to do when more than one resource needs to be created.  
- Makefile issues. Running the make build and the rest of the commands listed above do not work as it expects folders that do not exist and have dependencies (during a yarn install) that are unable to be found.
- schema.json only being able to handle primitive types in parameter definitions. Also does not support unions.