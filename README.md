#RSRC ABI
## Calling Convention
r31 is used as the stack pointer and initially points to the top of the stack
Arguments to a function are pushed in reverse order to the stack and then the
return address is pushed. r30 is used to hold the base pointer of a stack frame when a function gets called.
r0 will always be 0.
r20-r29 (inclusive) are callee save registers, the rest are caller save.
r19 stores the return value of the function
```
        Args to A
rb->    A's parent's bp
        A's return addr
        A's local vars
rsp->   Args to A's callees
```

## BNF
```
<program> ::= (<global-var-decl>)* (<function>)* <main>

<global-var-decl> ::= 'var ' <identifier> [ '=' <expression> ]
<function> ::= 'function ' <identifier> '(' ('var' <identifier> ',')* '){' 
                <block> '}'
<main> ::= 'function ' main '(){' <block> '}'

<block>         ::= (<statement>)*
<statement>     ::= <if> | <while> | <assignment> | <local-var-decl> | 
                    <function-call> | <return>
<if>            ::= 'if(' <expression> '){' <block> '}' ['else{' <block> '}']
<while>         ::= 'while(' <expression> '){' <block> '}'
<assignment>    ::= (<identifier>) '=' <expression>
<p-assignment>  ::= '@' '(' <expression> ')' '=' <expression>
<local-var-decl>::= 'var' <identifier> [ '=' <expression> ]
<function-call> ::= <identifier> '(' (<expression>,)* ')'
<return>        ::= 'return' ['(' <expression> ')']

<expression>    ::= <term> [<or-op> <term>]*
<term>          ::= <factor> [<and-op> <factor>]*
<factor>        ::= <not> <factor> | <relation>
<relation>      ::= <a-expression> [<rel-op> <a-expression>]
<a-expression>  ::= <a-term> [<add-op> <a-term>]*
<a-term>        ::= <a-factor> [<mul-op> <a-factor>]*
<a-factor>      ::= <add-op> <a-factor> | <literal> | <identifier> | 
                    <function-call> | '('<expression>')' | 
                    '@' '(' <expression> ')'
<or-op>         ::= '|' | '||'
<and-op>        ::= '&' | '&&'
<not>           ::= '~' | '!'
<rel-op>        ::= '<' | '>' | '<=' | '>=' | '==' | '!='
<add-op>        ::= '+' | '-' | '++' | '--'
<mul-op>        ::= '*' | '/' | '>>' | '<<'

<identifier> ::= [_A-Za-z][_A-Za-z0-9]*
```
