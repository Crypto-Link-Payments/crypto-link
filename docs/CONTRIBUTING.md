# Contributing to Crypto Link

## Code of Conduct 
By participating in contribution, you are expected to uphold this 
[Code of conduct](CODE_OF_CONDUCT.md) adapted from Contributors Convenant v2.0

## Setup Instructions
In order for Crypto Link to operate optimally, it is required to setup various files in main folder as well as 
install project requirements. You can access all details [here](PROJECTSETUP.md).

## Contribution Principles
## Fork the project to your computer
```bash
git clone https://github.com/launch-pad-investments/crypto-link.git
```


### Branch naming requirements

In order to make contribution easier for everyone each branch naming title needs to be readable and follow principles 
presented below:

```text
# Branch name constructs

<type>/<area>-<action>
```

Available ***type*** options:

- improvement
- bug 
- feature

Available ***area*** options:

- Docs  => Used when providing modifications/improvements or upgrades to github documentation
- Discord => Used when providing modifications/improvements or upgrades to part of the code (cogs folder)
- Backend =>  Used when making modifications/improvements or upgrades to backend files (mainly backend folder)
- Multi => Due to interconnection of scripts and development objectives modifications are required to be done to backend and cogs

Available ***action*** options:

Custom description with maximum 3 words separated by -

Example of creating the branch by following principles above

```text
git checkout -b docs/discord-owner-cmds
```

### PR naming and description
Try to be "on-point" with the title of the pull request so it can be clearly identified what it is all about. 
In its description provide as many details as possible on what you have worked on and make the reviews easier for 
maintainers. 


[System Commands](SYSTEMCOMMANDS.md)  | [Back to main page](README.md)
