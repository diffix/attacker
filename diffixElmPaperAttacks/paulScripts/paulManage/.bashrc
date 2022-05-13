# ~/.bashrc: executed by bash(1) for non-login shells.  -*-sh-*-

#
# this file is part of the confupdate system.
# if you want a bashrc of your own please create
# an alternative file, like /root/.bashrc.local, and
# then let the .bashrc symlink point to the new file.
# ( cd /root ; [ -L .bashrc ] && rm .bashrc ; ln -s .bashrc.local .bashrc )
# _OR_
# add your stuff to ~/.bashrc.d/XXX

export EDITOR=emacs
#export PYTHONPATH=${PYTHONPATH}:/root/paul/github/attacker/diffixElmPaperAttacks
export PYTHONPATH=/root/paul/github/attacker/diffixElmPaperAttacks/rpycTools:/root/paul/github/attacker/diffixElmPaperAttacks/diffAttack:/root/paul/github/attacker/diffixElmPaperAttacks/outlierBucket
export ATTACK_RESULTS_DIR=/root/paul/attackResults

# If not running interactively, don't do anything
[ -z "$PS1" ] && return

export PS1='\h:\w\$ '
umask 022

export LS_OPTIONS='--color=auto'
eval $(dircolors)
alias ls='ls $LS_OPTIONS'
alias ll='ls $LS_OPTIONS -lh'
alias la='ls $LS_OPTIONS -lha'
alias l='ls $LS_OPTIONS -lA'

alias     ..='cd ..'
alias   cd..='cd ..'
alias    ...='cd ../..'

alias     env='env | sort'

export HISTSIZE=10000
export HISTCONTROL=ignoreboth
export HISTTIMEFORMAT='%F_%T  '

if [ -z "$GUESS_ROOT" ] ; then
    if [ -n "$MPI_ROOT" ] ; then
        GUESS_ROOT="$MPI_ROOT"
    elif [ -n "$SUDO_USER" ] ; then
        GUESS_ROOT="$SUDO_USER"
    else
        GUESS_ROOT=$(pstree -upAl | perl -ne 'if (/\($$[,)]/){s/^(.*,\S+?\)).*$/$1/;s/.+?,(\S+?)\)/$1 /g;s/\s*$//s;if (/\($$[,)]/){$_=$ENV{"LOGNAME"}};print "$_\n"}' | xargs)
    fi
    export GUESS_ROOT
fi

if [ -d "$HOME/.bashrc.d" ] ; then
    shopt -s nullglob
    for file in $HOME/.bashrc.d/*.conf ; do
	if [ -r "$file" ] ; then
	    source "$file"
	fi
    done
    shopt -u nullglob
fi

if [ -r "$HOME/.bash_motd" ] ; then
    cat "$HOME/.bash_motd"
fi
