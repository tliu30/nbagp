def gplvm_likelihood(X, Y, log_hypers):

    N, observed_dimension = Y.size
    latent_dimension = X.size[1]

    K1_1 = mxsq(X); Dia = np.diag(K1_1)
    K1_2 = np.ones((N,1)) * Dia.T / 2
    K1_3 = Dia * np.ones((1,N)) / 2
    K1_4 = np.exp(log_hypers['gamma'])
    K1 = (K1_1 - K1_2 - K1_3) * K1_4

    K2 = np.exp(log_hypers['alpha'] + K1)
    K = K2 + np.eye(N) * np.max(np.exp(log_hypers['betainv']), 1e-3) # HACK

    tmp = (K \ Y) * Y.t # What does the backslash mean in matlab?
    gradLK = 0.5 .* (tmp - observed_dimension * np.eye(N)) / K
    f = 0.5 * observed_dimension * np.slogdet(K) + 0.5 * np.trace(tmp)

    grad_X = np.zeros( (N, latent_dimension) )
    for n1 in xrange(N):
        xn = X[n1,:]
        Kn = K[:,n1]
        grad_X[n1,:] = -1 * gradLK[n1,:] * 
            ((xn[ones(N,1),:] - X) .* Kn[:,np.ones((1,latent_dimension)]))

    grad_X = grad_X * -2 * np.exp(log_hypers['gamma'])

    log_hypers_grad = {}
    log_hypers_grad['alpha'] = -1 * np.sum(np.sum(gradLK .* K2))
    log_hypers_grad['betainv'] = -1 * np.exp(log_hypers['betainv']) * np.trace(gradLK)
    log_hypers_grad['gamma'] = -1 * np.sum(np.sum(gradLK .* (K1 .* K2)))

    return (f, grad_X, log_hypers_grad)

                    
