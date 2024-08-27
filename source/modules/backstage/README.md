# Connected Mobility Solution on AWS - Backstage Module
<!-- markdownlint-disable-next-line -->
**[Connected Mobility Solution on AWS](https://aws.amazon.com/solutions/implementations/connected-mobility-solution-on-aws/)** | **[🚧 Feature request](https://github.com/aws-solutions/connected-mobility-solution-on-aws/issues/new?assignees=&labels=enhancement&template=feature_request.md&title=)** | **[🐛 Bug Report](https://github.com/aws-solutions/connected-mobility-solution-on-aws/issues/new?assignees=&labels=bug&template=bug_report.md&title=)** | **[❓ General Question](https://github.com/aws-solutions/connected-mobility-solution-on-aws/issues/new?assignees=&labels=question&template=general_question.md&title=)**

**Note**: If you want to use the solution without building from source, navigate to the
[AWS Solution Page](https://aws.amazon.com/solutions/implementations/connected-mobility-solution-on-aws/).

## Table of Contents

- [Connected Mobility Solution on AWS - Backstage Module](#connected-mobility-solution-on-aws---backstage-module)
  - [Table of Contents](#table-of-contents)
  - [Solution Overview](#solution-overview)
  - [Architecture Diagram](#architecture-diagram)
  - [Sequence Diagram](#sequence-diagram)
  - [AWS CDK and Solutions Constructs](#aws-cdk-and-solutions-constructs)
  - [Customizing the Module](#customizing-the-module)
  - [Prerequisites](#prerequisites)
    - [MacOS Installation Instructions](#macos-installation-instructions)
    - [Clone the Repository](#clone-the-repository)
    - [Install Required Dependencies](#install-required-dependencies)
    - [Unit Test](#unit-test)
    - [Build the Module](#build-the-module)
    - [Upload Assets to S3](#upload-assets-to-s3)
    - [Deploy on AWS](#deploy-on-aws)
    - [Delete](#delete)
    - [Local Development](#local-development)
  - [Usage](#usage)
    - [S3 Buckets](#s3-buckets)
    - [Definitions](#definitions)
    - [Public / Published Solution Assets](#public--published-solution-assets)
    - [Local Solution Assets](#local-solution-assets)
  - [Cost Scaling](#cost-scaling)
  - [Collection of Operational Metrics](#collection-of-operational-metrics)
  - [License](#license)

## Solution Overview

The ACDP Backstage Module is an opinionated deployment of [Backstage](https://backstage.io/). Backstage provides a convenient
and functional interface to manage and deploy software. CMS modules are configured to be compatible with Backstage while
enabling deeper features into the Backstage design.

For more information and a detailed deployment guide, visit the
[ACDP Backstage Module](https://docs.aws.amazon.com/solutions/latest/connected-mobility-solution-on-aws/backstage-module.html)
Implementation Guide page.

## Architecture Diagram

![ACDP Backstage Architecture Diagram](./documentation/architecture/acdp-backstage-architecture-diagram.svg)

## Sequence Diagram

![CMS Module Deployment Sequence Diagram](./documentation/sequence/cms-module-deployment-sequence-diagram.svg)

## AWS CDK and Solutions Constructs

[AWS Cloud Development Kit (AWS CDK)](https://aws.amazon.com/cdk/) and
[AWS Solutions Constructs](https://aws.amazon.com/solutions/constructs/) make it easier to consistently create
well-architected infrastructure applications. All AWS Solutions Constructs are reviewed by AWS and use best
practices established by the AWS Well-Architected Framework.

In addition to the AWS Solutions Constructs, the solution uses AWS CDK directly to create infrastructure resources.

## Customizing the Module

## Prerequisites

- [Python 3.12+](https://www.python.org/downloads/)
- [NVM](https://github.com/nvm-sh/nvm)
- [NPM 8+](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
- [Node 18+](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
- [Pipenv](https://pipenv.pypa.io/en/latest/installation.html)

Required For Local Development Only:

- [Docker](https://www.docker.com/products/docker-desktop/)
- [Docker Compose v1](https://docs.docker.com/compose/install/) (v2 is included with Docker)

### MacOS Installation Instructions

Pyenv [Github Repository](https://github.com/pyenv/pyenv)

```bash
brew install pyenv
pyenv install 3.12
```

Pipenv [Github Repository](https://github.com/pypa/pipenv)

```bash
pip install --user pipenv
pipenv install --dev
```

NVM [Github Repository](https://github.com/nvm-sh/nvm)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
```

NPM/Node [Official Documentation](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)

```bash
nvm install 18
nvm use 18
```

For local development:

```bash
brew cask install docker
brew install docker-compose
```

### Clone the Repository

```bash
git clone https://github.com/aws-solutions/connected-mobility-solution-on-aws.git
cd connected-mobility-solution-on-aws/source/modules/backstage/cdk/
```

### Install Required Dependencies

```bash
make install
```

### Unit Test

After making changes, run unit tests to make sure added customization passes the tests:

```bash
make test
```

### Build the Module

The build script manages dependencies, builds required assets (e.g. packaged lambdas), and creates the
AWS Cloudformation templates.

```bash
make build
```

### Upload Assets to S3

```bash
make upload
```

### Deploy on AWS

Deployment should be done via the ACDP module deployment. This deployment creates a CodePipeline instance that deploys Backstage.

If manual deployment is desired, ensure ACDP is deployed and the proper environment variable configs are present and valid
via the Backstage Makefile. Understand there is risk of unsuccessful config and deployment.

```bash
make deploy
```

### Delete

```bash
make destroy
```

### Local Development

After installing dependencies, you can run backstage locally.
Note: All commands assume the PWD is [git_root]/source/modules/backstage

Start the postgres instance, backstage backend, and backstage frontend:

```bash
make run-backstage-local
```

There are Make targets available to separately run each component when required. Refer to the Makefile for these targets.

## Usage

### S3 Buckets

### Definitions

- Global Solution Assets
  - CloudFormation templates. Unique templates for each CMS module.
- Regional Solution Assets
  - Regional assets which support CloudFormation deployments. This is most often Lambda assets such as lambda layers and
    source code, but may also include other assets depending on the AWS services in use.
- Backstage Assets
  - Assets necessary for populating the initial Backstage catalog, and support deploying CMS modules from Backstage. This
    includes [software templates](https://backstage.io/docs/features/software-templates/), buildspecs to define deploy, update,
    and teardown, and [techdocs](https://backstage.io/docs/features/techdocs/) assets for each module.
- Backstage Catalog Items
  - Templates which define Backstage [catalog entities](https://backstage.io/docs/features/software-catalog/). This includes,
    the initial Catalog entities, such as the [software templates](https://backstage.io/docs/features/software-templates/),
    as well as entities generated during Backstage usage such as components and users. See the referenced Backstage catalog
    documentation for more details.

### Public / Published Solution Assets

| S3 Bucket | Description | Usage / Content |
|-----------|-------------|-------|
| Solutions Global Reference Bucket | Public, global, AWS Solution's reference bucket. | Global solution assets. |
| Solutions Regional Reference Bucket | Public, region specific, AWS Solution's reference bucket. | Regional solution assets and Backstage assets in the form of a Backstage zip. Backstage assets are not used from this location, but are included here to be copied into the Local Asset Bucket. | <!-- markdownlint-disable-line -->
| Local Asset Bucket | Backstage Catalog bucket created during deployment. | Backstage assets and Backstage catalog entities. Initially populated by copying the Backstage assets zip from the Solutions Regional Reference Bucket. | <!-- markdownlint-disable-line -->

### Local Solution Assets

| S3 Bucket | Description | Usage |
| :-------- | :---------- | :---- |
| acdp-assets-<account_id>-<aws_region> | Private bucket required to be created and populated to support Backstage local deployment. | Global and regional solution assets. Populated by building and uploading local assets. Also includes Backstage assets in the form of a Backstage zip. Backstage assets are not used from this location, but are included here to be copied into the Local Asset Bucket. | <!-- markdownlint-disable-line -->
| Local Asset Bucket | Backstage Catalog bucket created during deployment. | Backstage assets and Backstage catalog entities. Initially populated by copying the Backstage assets zip from the acdp-assets-<account_id>-<aws_region> bucket. | <!-- markdownlint-disable-line -->

## Cost Scaling

Cost will scale depending on the amount of templates and assets used, network traffic, and number of deployments.

- [Amazon S3 Cost](https://aws.amazon.com/s3/pricing/)
- [Amazon EC2 Cost](https://aws.amazon.com/ec2/pricing/)
- [Amazon ELB Cost](https://aws.amazon.com/elasticloadbalancing/pricing/)
- [Amazon CodeBuild Cost](https://aws.amazon.com/codebuild/pricing/)

For more details, see the
[implementation guide](https://docs.aws.amazon.com/solutions/latest/connected-mobility-solution-on-aws/cost.html).

## Collection of Operational Metrics

This solution collects anonymized operational metrics to help AWS improve
the quality and features of the solution. For more information, including
how to disable this capability, please see the
[implementation guide](https://docs.aws.amazon.com/solutions/latest/connected-mobility-solution-on-aws/anonymized-data-collection.html).

## License

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License").
You may not use this file except in compliance with the License.
You may obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
