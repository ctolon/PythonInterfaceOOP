# Prerequisites!!!

@tableofcontents

## Cloning repository

Clone Repository in your workspace:

```ruby
git clone https://github.com/ctolon/PythonInterfaceDemo.git
```

Then go NewAllWorkFlows folder with `cd` commands

Since the scripts are still in development, it is recommended to update daily regularly with the following command:

```ruby
git pull --rebase
```

## argcomplete - Bash tab completion for argparse

If you are using a linux based system or working on LXPLUS (like Ubuntu, Fedora CentOS), follow the instructions for Linux. If you are using a MacOS-based system, follow the instructions for MacOS.

Argcomplete provides easy, extensible command line tab completion of arguments for your Python script.

It makes two assumptions:

    You’re using bash as your shell (limited support for zsh, fish, and tcsh is available)

    You’re using argparse to manage your command line arguments/options

Argcomplete is particularly useful if your program has lots of options or subparsers, and if your program can dynamically suggest completions for your argument/option values (for example, if the user is browsing resources over the network).

Owner of Orginal Code: `Andrey Kislyuk` 
Licensed under the terms of the Apache License, Version 2.0.

Orginal Documentation:

https://kislyuk.github.io/argcomplete/index.html#

## Instalation Guide For argcomplete

### Prerequisites Before Installation argcomplete Package For Linux Based Systems and LXPLUS

Global completion requires bash support for complete -D, which was introduced in bash 4.2. Older Linux systems, you will need to update bash to use this feature. Check the shell type with `echo $SHEL` . If it's bash, Check the version of the running copy of bash with `echo $BASH_VERSION`. If your bash version older than 4.2 you need the update your bash:

Update Bash on CentOS/Redhat/Fedora Linux:

```ruby
yum update bash
```

Update Bash in Ubuntu / Debian / Linux Mint:

```ruby
apt-get install --only-upgrade bash
```

Also you need check your shell type with `echo $SHEL`. if your shell isn't bash you need change your shell with (if your shell type is bash you don't need to use these commands):

```ruby
exec bash
```

(It just changes the type of terminal you are working in, the system's main shell settings are preserved)

or

```ruby
sudo chsh -s /bin/bash <username> 
```

or 

```ruby
 sudo chsh -s /bin/bash
```

(Converts all system shell settings to bash)

IMPORTANT P.S 1 : If you use the `exec` bash command you will need to use this command every time when you open a new terminal to for source the argcomplete.sh script.

IMPORTANT P.S 2 : If you cannot source the `argcomplete.sh` script even though you are using the `exec bash` command, use the `sudo chsh -s /bin/bash` command. This command will change the shell settings of the entire system. When you're done with O2-DQ Scripts, you can similarly use `sudo chsh -s /bin/<shelltype>` to return to your old shell system. For example, if your host's default shell configuration is `zsh`, you can restore the system with `sudo chsh -s /bin/zsh`


### Local Instalation (Not Need For O2)

For Local İnstallation (If you have virtual env, disable it first)

```ruby
pip install argcomplete
activate-global-python-argcomplete
```

### O2 Installation

For in O2

Firstly, activate your Alienv e.g.

```ruby
alienv enter O2Physics/latest-master-o2
```

Then install the package:

```ruby
pip install argcomplete
```

And go your Folder which includes your run scripts with cd commands (e.g.):

```ruby
cd ~/NewAllWorkFlows
```


And then, source your argcomplete script for autocomplete:

```ruby
source argcomplete.sh
```

VERY IMPORTANT P.S This script must be re-sourced every time you re-enter the O2 environment!!! (For autocompletion with TAB key)

### Prerequisites Before Installation argcomplete Package For MacOS Based Systems

Global completion requires bash support for complete -D, which was introduced in bash 4.2. On OS X, you will need to install and update bash to use this feature. On OS X, install bash via Homebrew `brew install bash`, add /usr/local/bin/bash to /etc/shells, then run `exec bash` to switch bash shell temporary (temporarily applies to the terminal you are working in, does not change your shell system settings). if you still have problems with sourcing the argcomplete.sh script, use this command instead `sudo chsh -s /bin/bash` or `sudo chsh -s /bin/bash <username>`. This will change the shell settings of the whole system and for example if your system used zsh based shell before to go back, you can use the command `sudo chsh -s /bin/zsh <username>` or `sudo chsh -s /bin/zsh`.

### Local Instalation (Not Need For O2)

```ruby
brew install bash
```
For Local İnstallation (If you have virtual env, disable it first)

```ruby
pip install argcomplete 
```

or 

```ruby
pip3 install argcomplete 
```

(depends on symbolic link of python. It is recommended to install with both options)

```ruby
activate-global-python-argcomplete
```

### O2 Installation

Install and update your bash shell with this command:

```ruby
brew install bash
```

Then check your shell with this command:

```ruby
echo $SHEL
```

If your shell isn't bash (The default shell for macOS is zsh, not bash. Most likely your shell type is zsh), you need change your bash with this commands:

```ruby
exec bash
```

(It just changes the type of terminal you are working in, the system's main shell settings are preserved)

or

```ruby
sudo chsh -s /bin/bash <username> 
```

or  

```ruby
sudo chsh -s /bin/bash
```

(Converts all system shell settings to bash)

After then, Check the version of the running copy of bash with `echo $BASH_VERSION`. It must be greater than 4.2.

IMPORTANT P.S 1 : If you use the `exec` bash command you will need to use this command every time when you open a new terminal to for source the argcomplete.sh script.

IMPORTANT P.S 2 : If you cannot source the `argcomplete.sh` script even though you are using the `exec bash` command, use the `sudo chsh -s /bin/bash` command. This command will change the shell settings of the entire system. When you're done with O2-DQ Scripts, you can similarly use `sudo chsh -s /bin/<shelltype>` to return to your old shell system. For example, if your host's default shell configuration is `zsh`, you can restore the system with `sudo chsh -s /bin/zsh`

For in O2

Firstly, activate your Alienv e.g.

```ruby
alienv enter O2Physics/latest-master-o2
```

Then install the package:

```ruby
pip install argcomplete 
```

or 

```ruby
pip3 install argcomplete
```

(depends on symbolic link of python. It is recommended to install with both options)

And go your Folder which includes your run scripts with cd commands (e.g.):

```ruby
cd ~/NewAllWorkFlows
```

And then, source your argcomplete script for autocomplete:

```ruby
source argcomplete.sh
```

VERY IMPORTANT P.S This script must be re-sourced every time you re-enter the O2 environment!!! (For autocompletion with TAB key)

[← Go back to Python Scripts And JSON Configs ](1_ScriptsAndConfigs.md) | [↑ Go to the Table of Content ↑](../README.md) | [Continue to Instructions for TAB Autocomplete →](3_InstructionsforTABAutocomplete.md)
