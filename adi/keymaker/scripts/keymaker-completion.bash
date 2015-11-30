# this file gives `keymaker` autocomplete.  it'll output optional keyword
# arguments as well as roles, *if* your current AWS credentials permit listing
# roles.  If it doesn't, it'll fail quietly.

role_cache=/tmp/keymaker-roles
role_cache_age=30

get_roles()
{
    aws iam list-roles 2> /dev/null | awk -F: '/RoleName/ {print substr($2, 3, length($2)-5)}' > $role_cache
}

get_options()
{
    keymaker -h 2>&1 | grep -oG "\(--[^\ ]*\)" | sort -u
}

_keymaker()
{
    local cur prev
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    if [ ! -f $role_cache ]; then
        get_roles
    elif [ "$(find $role_cache -mmin +${role_cache_age})" ]; then
        get_roles
    fi

    case "${cur}" in
        -*)
            COMPREPLY=( $(compgen -W "$(get_options)" -- ${cur}) )
            return 0
            ;;
        *)
            COMPREPLY=( $(compgen -W "$(cat $role_cache)" -- ${cur}) )
            return 0
            ;;
    esac
}
complete -F _keymaker keymaker

alias keymaker-reset='unset $(env | grep "^AWS" | cut -d= -f 1)'
alias keymaker-show='env | grep "^AWS"'
