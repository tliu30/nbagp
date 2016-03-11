# So does this do one step of hybrid / hamiltonian mc?
def hmc(likefunc, x, options, labels, *args):

    arate = 0
    num_iters = options['num_iters']
    E, g = likefunc(x, *args)

    for l in xrange(num_iters):
        p = randn( x.shape ) # random normal
        H = p.T * p / 2 + E

        xnew = x
        gnew = g

        cur_tau = randi(options['Tau']) # Random uniform?
        cur_eps = rand * options['epsilon'] # Another random...

        for tau in xrange(cur_tau):
            p = p - cur_eps * gnew / 2
            xnew = xnew + cur_eps * p
            ignore, gnew = likefunc(xnew, *args)
            p = p - cur_eps * gnew / 2

        Enew, ignore = likefunc(xnew, *args)
        Hnew = p.T * p / 2 + Enew
        dh = Hnew - H

        if dh < 0:
            accept = 1
            print 'a' # print statement???
        else:
            if rand() < np.exp(-1 * dh): # rand uniform?
                accept = 1
                print 'A' #pirnt statement?
            else:
                accept = 0
                print 'r' #print statement

    arate = arate / num_iters
    params = x
    nll = E

    return (params, nll, arate)
