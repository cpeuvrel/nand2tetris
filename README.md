## Le MOOC

MOOC de l'université de Jerusalem `From Nand to Tetris`
Explique comment fonctionne un ordinateur
Part au niveau micro-electronique et finissant à l'OS

Aucun prérequis, à part logique de base (AND/OR/NOT)
Part de la porte NAND -> systèmes plus complexe jusqu'à CPU et mémoire

## Portes logiques basiques

- NOT
- AND
- OR
- XOR

Multiplexer (MUX): a AND NOT sel OR b AND sel
Demultiplexer (DMux)

### Portes logiques multi-bits

- Not 8bits: 8 inputs, 8 out
- Or 8bits: 16 inputs(`8*a, 8*b`), 8 out: out[N] = a[N] OR b[N]
- And 8bits: 16 inputs(`8*a, 8*b`), 8 out
- Mux 8 bits: 16 inputs(`8*a, 8*b`) + 1 selector, 8 out

### Portes logiques multi-ways

- Or 8way: 8 inputs, 1 out. Out=1 si au moins 1 input == 1
- And 8way: 8 inputs, 1 out. Out=1 si tout input == 1
- 4Way Mux: `4*16` inputs + 2 selector, 16 out

```
sel[1]  sel[0]  ||  out
-----------------------
0         0     ||  a
0         1     ||  b
1         0     ||  c
1         1     ||  d
```

- 4Way DMux: 16 inputs + 2 selector, `16*4` out

```
sel[1]  sel[0]  ||  a  b  c  d
-----------------------
0         0     ||  in 0  0  0
0         1     ||  0  in 0  0
1         0     ||  0  0  in 0
1         1     ||  0  0  0  in
```

## Puces plus complexes

Adder: puce additionnant n bits (problème du overflow)

ALU (Arithmetic Logical Unit): pouvoir faire addition, multiplication, ...
- 2 n-bits inputs
- 1 n-bits output
- quelques bits pour controller la fonction à utiliser sur les 2 inputs
    - zx/zy: force x/y à 0
    - nx/ny: force x/y à not x/not y
    - f: choisi si out = x+y / x&y
    - no: force out = not out
- quelques bits de contrôle sur le résultat (résultat 0, résultat négatif)

## Mémoire

Data Flip-Flop, 2e (et dernière) brique de base: out(t) = in(t-1)
Basé sur une clock unique (CPU à 3GHz)

Binary cell (Bit): avec un Mux on dit: quand sel=1 -> on enregistre data, sinon on continue à donner la même data
Registre: n-bits Bit

### RAM

/*
- 16bits input
- load bit flag
- adress (log2(n) bits)
- 16bits output

=> out(t) = RAM[adress(t)](t)
=> if load(t-1):
      RAM[address(t-1)](t) = in(t-1)
  */

### Résultat mémoire

On se retrouve avec 2 principales mémoires:
- les registres: peu nombreux (~15aine), mémoire de travail du processeur, facilement accessible
- la RAM: large mémoire (ici ~16k), mais plus complexe d'accès, et en vrai plus lente
    - data: une partie réserver pour stocker des données arbitraire
    - program: une partie pour stocker les instructions du programme à exec

## Assembler

Un programme est une liste d'instruction bas-niveau:
- arithmetique/logique: ADD R2, R1, R3 (enregistre en R2 `R1+R3`), AND, ...
- Accès mémoire
    - LOAD R1, 67 (registre R1 = contenu de la mémoire à l'adresse 67)
    - LOADI R1, 67 (registre R1 = 67)
    - accès indirect (pointeur)
- Contrôle: jump conditionnel ou non

### Instructions

Langage binaire du CPU. 16bits
- 1: instruction sinon valeure
- 2-3: non utilisé
- 4-10: code de l'instruction
- 11-13: registre de destination
- 14-16: jump

### I/O

Pour gérer les accès aux I/O (écran, clavier, ...), on définit certaines parti de la mémoire comme étant des représentations de ce périphérique (exemple pixel écran, ou code touche clavier)

## CPU

Il ne reste plus qu'à assembler tout ça pour avoir un ordinateur très basique.
On précharge la partie `program` de la RAM avec ce qu'on veut exécuter et on peut démarrer l'execution 

## Pour plus d'info

- [TED Talk](https://www.ted.com/talks/shimon_schocken_the_self_organizing_computer_course?language=en)
- [Nand2Tetris website](https://www.nand2tetris.org/)
