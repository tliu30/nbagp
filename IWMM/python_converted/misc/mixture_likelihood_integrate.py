def mixture_likelihood_integrate(X, resp, prior):
    N, latent_dimension = X.size
    n_components = resp.size[1]

    prior['r'] = 1
    prior['nu'] = 1
    prior['S'] = np.eye(latent_dimension)
    prior['m'] = np.zeros( (1, latent_dimension) )

    nll = 0
    dnll_X = np.zeros( (N, latent_dimension) )

    for z in xrange(n_components):
        n = np.sum(resp[:,z], 0); # Check the axis use...
        Xz = X[find(resp[:,z] == 1), :]
        C = mxsq(Xz)
        rprime = prior['r'] + n
        nuprime = prior['nu'] + n
        mprime = (prior['r'] * prior['m'] + np.sum(Xz,0)) / (prior['r'] + n)
        Sprime = prior['S'] + C + prior['r'] * mxsq(prior['m']) - rprime * mxsq(mprime)
        L = 0.5 * nuprime * np.slogdet( Sprime ) # check out slogdet in numpy...
        nll = nll + L

        invSprime = np.inv(Sprime) # make sure i can invert like this
        dnll_X[find(resp[:,z] === 1), :] = dnll_X[find(resp[:,z] == 1),:] + 
            nuprime * (Xz - repmat(rprime / (prior['r']  + n).^2 * 
            (prior['r'] * prior['m'] + np.sum(Xz)), n, 1)) * invSprime

    return nll, dnll_X


