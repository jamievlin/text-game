grammar DialogScript;

options {
    language=Python3;
}

WHITESPACE: [ \t\r\n]+ -> skip;

fragment CHARACTER: [a-zA-Z];
fragment NUMBER: [0-9];

fragment UNDERSCORE: '_';
fragment ESCAPE_SEQ: '\\'[btnfr"'\\$];

fragment STRING_CHARACTER: ~["\\\r\n] | ESCAPE_SEQ;
fragment STRING_ML_CHARCTER: ~["\\] | ESCAPE_SEQ;

fragment SEMICOLON: ';';
STM_END: SEMICOLON;

PARENTHESES_BEGIN: '(';
PARENTHESES_END: ')';

// constants
fragment TRUE: 'true';
fragment FALSE: 'false';
BOOLEAN_CONST: TRUE | FALSE;

// keywords
SAY: 'say' | 'says';
BEGIN: 'begin';
END: 'end';

MODULE: 'module';
BLOCK: 'block';
OPTIONS: 'options';
OPTION: 'option' | 'opt';

COLON: ':';
BIG_ARROW: '=>';
NOP: 'nop';

// control keywords
GOTO: 'goto';
EXIT: 'exit';

LET: 'let';

EQ_ASSIGN: '=';

// operators
EQ_OPERATOR: '==';
AND_OPERATOR: '&&' | 'and';
OR_OPERATOR: '||' | 'or';

// string literals
INIT_IDENTIFIER_CHAR: CHARACTER | UNDERSCORE;
fragment STRING_ML: '"""' STRING_ML_CHARCTER+ '"""';
fragment STRING_SL: '"' STRING_CHARACTER+ '"';

// values
STRING_LIT: STRING_ML | STRING_SL;
IDENTIFIER: INIT_IDENTIFIER_CHAR (INIT_IDENTIFIER_CHAR | NUMBER)*;
NUMBERS: NUMBER+;

// statements

say: IDENTIFIER SAY STRING_LIT;

// control statements
goto: GOTO IDENTIFIER;

// options
option_inert:
    OPTION NUMBERS STRING_LIT;

option_single_stm: OPTION NUMBERS STRING_LIT BIG_ARROW statement;

option_stm:
    BEGIN OPTION NUMBERS STRING_LIT
    (statement STM_END)*
    END;

binary_op
    : EQ_OPERATOR
    | AND_OPERATOR
    | OR_OPERATOR
    ;

option
    : option_inert
    | option_stm
    | option_single_stm
    ;

opts:
    BEGIN OPTIONS
    (option STM_END)+
    END;

statement
    : goto
    | say
    | opts
    | assignment
    | value
    | NOP
    | EXIT
    ;

block:
    BEGIN BLOCK IDENTIFIER
    (statement STM_END)*
    END STM_END;

literal: NUMBERS | BOOLEAN_CONST | STRING_LIT;

value
    : literal                   # processLiteral
    | PARENTHESES_BEGIN value PARENTHESES_END   # processParentheses
    | value binary_op value     # processBinaryOp
    ;

assignment: IDENTIFIER EQ_ASSIGN value;

vardecs:
    LET IDENTIFIER
    ;

litvardecs:
    LET IDENTIFIER (EQ_ASSIGN literal)? STM_END;

global_stm
    : block        # processBlock
    | litvardecs   # processGlobalVarDecs
    ;


root: global_stm+ EOF;
