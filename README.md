# sat2vc
The program **sat2vc** transforms instances of the SAT 
problem [[1]](#References)  given in the DIMACS 
format [[4]](#References) into instances of the Vertex 
Cover [[2]](#References) problem in the PACE graph 
format [[5]](#References). The transformation uses a
the standard reduction by  Richard Karp [[3]](#References). 
It reduces instances from CNF-SAT to 3CNF-SAT and then reduces
directly to SAT by concatenated the reductions by Karp. 

(The reduction does additionally produce an instance of the 
clique problem, which was the case in the original reduction
by reducing SAT-> CLIQUE, CLIQUE -> VC).


## Download:
```bash
git clone git@github.com:daajoe/sat2vc.git
````

## References

1) [SAT Problem](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem)
2) [Vertex Cover Problem](https://en.wikipedia.org/wiki/Vertex_cover)
3) Richard M. Karp (1972). "Reducibility Among Combinatorial Problems" (PDF). In R. E. Miller; J. W. Thatcher; J.D. Bohlinger (eds.). Complexity of Computer Computations. New York: Plenum. pp. 85–103. [doi:10.1007/978-1-4684-2001-2_9](https://link.springer.com/chapter/10.1007%2F978-1-4684-2001-2_9).
4) [DIMACS CNF format .cnf](http://www.satcompetition.org/2009/format-benchmarks2009.html)
5) [PACE graph format .gr](https://pacechallenge.org/2019/vc/vc_format/)