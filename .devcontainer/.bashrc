custom_prompt() {
    # 色の定義（背景付き）
    RED=$'\033[41;37m'        # 赤背景に白文字（警告用）
    CYAN=$'\033[46;30m'       # 水色背景に黒文字
    YELLOW=$'\033[43;30m'     # 黄色背景に黒文字
    MAGENTA=$'\033[45;37m'    # マゼンタ背景に白文字
    GREEN=$'\033[42;30m'      # 緑背景に黒文字
    BLUE=$'\033[44;37m'       # **青背景に白文字** (新規追加)
    NC=$'\033[0m'             # 色リセット

    # 🚨 警告アイコンと背景色の定義
    WARNING_BG=$'\033[41;37m' # 赤背景に白文字
    WARNING_ICON=" 💀 "

    # 🛠️ ヘルパー関数
    format_text() {
        local text="$1"
        local color="$2"
        echo "${color}${text}${NC}"
    }

    # 🌎 各要素をキャッシュから取得
    local study_text="📚 CLOUD-ENGINEER-SCHOOL"
    local region_text="🌎 ${AWS_REGION:-unknown}"  # AWS_REGION のキャッシュ

    # 🏢 AWSアカウントIDのチェックと表示形式の決定
    local current_account="${AWSSTUDY_ACCOUNT_ID:-unknown}"  # AWSSTUDY_ACCOUNT_ID のキャッシュ
    local expected_account="101313435800"

    if [ "$current_account" = "unknown" ]; then
        local account_text="${WARNING_ICON} devcontainer を再起動してください ${WARNING_ICON}"
        local account_color="${WARNING_BG}"
    elif [ "$current_account" != "$expected_account" ]; then
        local account_text="\n${WARNING_ICON} ${current_account}は非対象アカウント: ${WARNING_ICON}\n ホストマシン上で perman-aws-vault select でアカウントを選択し、devcontainer を再起動してください\n"
        local account_color="${WARNING_BG}"
    else
        local account_text="🧏 ${current_account}"
        local account_color="${MAGENTA}"
    fi

    local pwd_text="📂 ${PWD}"

    # 🎨 色付きテキストを作成
    local study_indicator="$(format_text "${study_text}" "${GREEN}")"
    local formatted_region="$(format_text "${region_text}" "${CYAN}")"
    local formatted_account="$(format_text "${account_text}" "${account_color}")"
    local formatted_pwd="$(format_text "${pwd_text}" "${BLUE}")"

    # 🖥️ 出力（スペース幅を調整）
    printf "%b  %b  %b  %b" "${study_indicator}" "${formatted_region}" "${formatted_account}" "${formatted_pwd}"
}

# 🔄 AWS認証情報の更新スクリプトを読み込み
if [ -f /workspace/.devcontainer/update-credentials.sh ]; then
    source /workspace/.devcontainer/update-credentials.sh
fi

# 🚀 初回読み込み時に AWS の情報を取得してキャッシュ
initialize_prompt_cache() {
    export AWS_REGION=$(aws configure get region 2>/dev/null || echo "unknown")
    export AWSSTUDY_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text 2>/dev/null || echo "unknown")
}
initialize_prompt_cache

# ⚙️ PS1の設定 (`\w` を削除し、custom_prompt のみを使用)
PS1='$(custom_prompt)\n\$ '

# 🔑 SSH キー作成する際の名前を社員番号にする
export KEY_NAME=$(aws sts get-caller-identity | jq -r '.Arn | split("/")[-1]')

# 🖥️ AWSコマンド補完
complete -C '/usr/local/bin/aws_completer' aws

# 🖥️ Bashコマンド補完
source /etc/profile.d/bash_completion.sh

# 🖥️ CDKコマンド補完
_cdk_yargs_completions()
{
    local cur_word args type_list

    cur_word="${COMP_WORDS[COMP_CWORD]}"
    args=("${COMP_WORDS[@]}")

    # ask yargs to generate completions.
    type_list=$(cdk --get-yargs-completions "${args[@]}")

    COMPREPLY=( $(compgen -W "${type_list}" -- ${cur_word}) )

    # if no match was found, fall back to filename completion
    if [ ${#COMPREPLY[@]} -eq 0 ]; then
      COMPREPLY=()
    fi

    return 0
}
complete -o default -F _cdk_yargs_completions cdk

# 📄 ls のカラー出力を有効化
alias ls='ls --color=auto'
alias grep='grep --color=always'