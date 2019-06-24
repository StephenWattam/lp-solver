\CPLEX> enter example
\Enter new problem ['end' on a separate line terminates]:
maximize
3 x1 + 2 x2
subject to
2 x1 + x2 <= 100
x1 + x2 <= 80
x1 <= 40
bounds
0 <= x1
0 <= x2
end
\
\CPLEX> optimize
\Tried aggregator 1 time.
\LP Presolve eliminated 1 rows and 0 columns.
\Reduced LP has 2 rows, 2 columns, and 4 nonzeros.
\Presolve time = 0.00 sec.
\
\Iteration log . . .
\Iteration: 1 Dual infeasibility = 0.500000
\Iteration: 3 Dual objective = 180.000000
\
\Dual simplex - Optimal: Objective = 1.8000000000e+02
\Solution time = 0.00 sec. Iterations = 3 (2)
\
\CPLEX> display solution variables x1-x2
\Variable Name Solution Value
\x1 20.000000
\x2 60.000000
\
\CPLEX>
