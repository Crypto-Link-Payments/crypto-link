# Contributing to Crypto Link

## Code of Conduct 
By participating in contribution, you are expected to uphold this 
[Code of conduct](CODE_OF_CONDUCT.md) adapted from Contributors Convenant v2.0

## Setup Instructions
In order for Crypto Link to operate optimally, it is required to setup various files in main folder as well as 
install project requirements. You can access all details [here](PROJECTSETUP.md).

## Guidelines for contribution
At this stage we do not want to complicate contribution guidelines so steps are quite simple.

### Fork the project to your computer
```bash
git clone https://github.com/launch-pad-investments/crypto-link.git
```

### Create upstream 

```bash
cd crypto-link

git remote add upstream https://github.com/launch-pad-investments/crypto-link.git
```

You will have two remotes set-up. Origin which will point to your GitHub for of the project (Read and Write perm.), and 
upstream which points to the main project's GitHub repository (Read only)

### One Branch For Each piece of work and commit naming

Pull latest commits from master to get latest commits

```bash
git checkout master
git pull upstream master $$ git push origin master
```

It is important to put each piece of work on its own branch unless otherwise agreed with project owner. So far the project
has only __master__ branch to which all pull requests are merged. Check as well issues to identify if something 
has been discussed already. 

In order to make branch titles readable branch naming needs to follow patter:
```text
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

Create new branch following branch naming principles

```text
git checkout -b type/area-action

# Example

git checkout -b docs/discord-owner-cmds
```

Start coding and committing. Be sure to provide good commit messages as well to make maintainers lives 
easier. 

> Before you initiate PR run the local copy of Crypto Link in order to be sure that you have not broken anything.
> Ensure as well that you are fixing only the things you are working on as your PR might get rejected. Help
> developers minimize conflicts in advance. 

### Create a PR

when you are done coding and everything has been tested, you are required to push your branch to the origin remote
and click few buttons on the github 

First push a new branch which will create branch on your github project:
```text
git push -u origin docs/discord-owner-cmds
```

afterwards navigate to your fork of the project in browser and you will see on top ***Compare & Pull Request***
button . Open a pull request,, provide logical title as well as much information as possible on what you have worked.
When you are done press __Create pull request__ . After successfully initiated pull request, developers will review it
 and either provide some comments, request change or merge it. 

## Crypto Link System Commands Interface
Crypto Link has certain commands locked only for the project maintainers/owners. If you have setup botSetup.json file
details correctly than this commands will be available as well to you. Those commands are used to set up 
system fees, apply various settings, check bot's hot wallet and off chain wallet state, etc. 
We have mapped them out [here](SYSTEMCOMMANDS.md) 


[Back to main page](README.md)
