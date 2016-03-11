def gplvm_original(Y, latent_dimension, gplvm_options):
    # addpath('minFunc') - signifies we're also using these functions...

    N, D = Y.shape

    # Center the data
    Y = Y - np.rep( np.mean(Y), (N, 1) ) # is the broadcasting okay?

    # Initialize X through PCA
    log_hypers = {'alpha' : 0, 'betainv' : 0, 'gamma' : 0}
    params = {'X' : None} # is this actually local in matlab?
    if D == latent_dimension:
        params['X'] = Y
    else:
        svd1, _, _ = np.linalg.svd( Y, 0 )
        params['X'] = svd1[:, 1:latent_dimension]

    # Initialize some params
    gplvm_options['useMex'] = 0
    if 'maxFunEvals' not in gplvm_options:
        gplvm_options['maxFunEvals'] = 100
    gplvm_options['Display'] = 'off'

    # unwrap params???

    # should use some python specific optimizers rather than writing my own...
    params = minFunc(gplvm_original_likelihood, params, log_hypers, gplvm_options, Y, params)

    return params

