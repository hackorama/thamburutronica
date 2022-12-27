# Setup Typescript

```shell
$ brew install nvm
$ mkdir ~/.nvm
$ tail .zshenv
export NVM_DIR="$HOME/.nvm"
  [ -s "/opt/brew/opt/nvm/nvm.sh" ] && \. "/opt/brew/opt/nvm/nvm.sh"  # This loads nvm
  [ -s "/opt/brew/opt/nvm/etc/bash_completion.d/nvm" ] && \. "/opt/brew/opt/nvm/etc/bash_completion.d/nvm"  # This loads nvm bash_completion
```

```shell
$ node -v
v19.0.0
$ npm -v
8.19.2
```

```shell
$ npm install -g typescript
```

```shell
$ tsc -v
Version 4.8.4
```

```shell
$ tsc script.ts
```

```shell
$ cat tsconfig.json
{
  "compilerOptions": {
    "outDir": "static",
    "lib": [
      "es2015",
      "dom"
    ]
  },
  "files": [
    "script.ts"
  ]
}
```

```shell
$ ls static/script.*

$ tsc --strict

$ ls static/script.*
script.js
```

```shell
$ npm install prettier
$ npx prettier --write script.ts
```
