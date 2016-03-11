def sampling_dphyperparameter(alpha, n, k, a, b)
    """
    alpha - Dirichlet process hyperparameter
    n - number of samples
    k - number of clusters
    a,b - beta prior parameters for alpha
    """
    num_iters = 20
    for i in xrange(num_iters):
        eta = betarnd(alpha+1,n) # scipy.stats.beta.rvs()
        s = binornd(1, (a+k-1)/(a+k-1+n*(b-log(eta)))) # scipy.stats.binom.rvs()
        alpha = gamrnd(a+k+s-1,b-log(eta)) # scipy.stats.gamma.rvs()

    return alpha
