#RSRC ABI
## Calling Convention
r31 is used as the stack pointer and initially points to the top of the stack
Arguments to a function are pushed in reverse order to the stack and then the
return address is pushed. r30 is used to temporarily hold the return address
before it gets pushed.
r0 will always be 0.
r20-r29 (inclusive) are callee save registers, the rest are caller save.
r19 stores the return value of the function

## BNF
```
<program> ::= (<global-var-decl>)* (<function>)* <main>

<global-var-decl> ::= 'var ' <identifier> [ '=' <expression> ]
<function> ::= 'function ' <identifier> '(' (<identifier>)* '){' <block> '}'
<main> ::= 'function ' main '(){' <block> '}'

<block>         ::= (<statement>)*
<statement>     ::= <if> | <while> | <assignment> | <local-var-decl>
<if>            ::= 'if(' <expression> '){' <block> '}'
<while>         ::= 'while(' <expression> '){' <block> '}'
<assignment>    ::= <identifier> '=' <expression>
<local-var-decl>::= 'var' <identifier> [ '=' <expression> ]

<expression>    ::= <term> [<or-op> <term>]*
<term>          ::= <factor> [<and-op> <factor>]*
<factor>        ::= [<not>] <factor> | <literal> | <var> | <relation>
<relation>      ::= <a-expression> [<rel-op> <a-expression>]
<a-expression>  ::= <a-term> [<add-op> <a-term>]*
<a-term>        ::= <a-factor> [<mul-op> <a-factor>]*
<a-factor>      ::= [<add-op>] <a-factor> | <literal> | <var> | (expression)
<or-op>         ::= '|' | '||'
<and-op>        ::= '&' | '&&'
<not>           ::= '~' | '!'
<rel-op>        ::= '<' | '>' | '<=' | '>=' | '==' | '!='
<add-op>        ::= '+' | '-' | '++' | '--'
<mul-op>        ::= '*' | '/' | '>>' | '<<'

<identifier> ::= [_A-Za-z][_A-Za-z0-9]*
```
