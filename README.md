# blurg-liger

blurg is a command-line utility that manages diaries. Diaries may be stored locally, or they may be shared remotely through a server.

## Installation and Development

```
git clone https://github.com/jbshep/blurg
cd blurg
virtualenv -p python3 env
source blurg.env
pip install -r requirements.txt
```

Each team has its own Slack channel that corresponds to its project name.  The project also has a [UML diagram](doc/blurg.mdj) that serves as a good API reference.  The UML diagram should be kept up to date during each milestone using StarUML.

## Run

In one shell window, run the server.

``` 
source blurg.env
./run-server.sh
``` 

In another shell window, run the client.

```
source blurg.env
blurg <command> <args>
```

where &lt;command&gt; is one of:
* log
* key
* rm
* ls
* switch
* diaries
* wipe
* connect
* promote
* demote

**Note: Local vs. Remote diaries**

This program supports diaries that are stored locally and diaries that are accessed over the internet through the included server.
To switch between local diaries and remote diaries, use the `switch` subcommand.

Diaries can only be named with one word. If more words are entered for the name of a diary it will just name the diary after 
the first word.

* local: ```blurg switch <diaryname>```

* remote: ```blurg switch --remote=<URL> --user=<username> <diaryname>```
      
Where:
* `<diaryname>` is the name of the diary you want to create
* `<URL>` is the URL of the server you want to connect to
* `<username>` is the username that your entries will be stored under for a given diary

**Note: Connect**

Connect allows a user to connect to another users remote diary as long as they were given the key.
Be careful who you give your key out to. Once another user has access to the diary
they are able to see all the entries and wipe the diary without any problem. Use the key command
to get the current remote diary key.
	
* connect: ```blurg connect --remote=<URL> --user=<username> --key=<diarykey>```

Where:
* `<URL>` is the URL of the server you want to connect to
* `<username>` is the username that your entries will be stored under for a given diary
* `<key>` is the key of the remote diary you are trying to connect to

**Note: Promote and Demote**

Promote allows the user to move a local diary and all its log entriest to a remote. Demote allows 
the user to move a remote diary and all its entries from its server a local diary of the same 
name and then wipe it from the server.
	
* promote: ```blurg promote <localdiaryname> --remote=<URL> --user=<username>```
* demote: ```blurg demote <remotediaryname>```

Where:
* `<localdiaryname>` is the name of the local diary you'd like to promote
* `<remotediaryname>` is the name of the remote diary you'd like to demote
* `<URL>` is the URL of the server you want to connect to
* `<username>` is the username that your entries will be stored under for a given diary
## Tests

In one shell window:

```
source blurg.env
./run-server.sh
```

In another shell window, run the tests.

```
source blurg.env
pytest tests
coverage run -m pytest tests
coverage report -m
```
