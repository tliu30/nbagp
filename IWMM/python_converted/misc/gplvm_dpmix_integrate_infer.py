NUM_ITERS = 10000

DEFAULT_GPLVM_DPMIX_INTEGRATE_INFER_OPTIONS = {
    "isDP" : 1,
    "isGP" : 1,
    "isSamplingDPparameter" : 0,
    "isPlot" : 1,
    "isFixedGauss" : 0,
    "isGPLVMinit" : 0,
    "isMovie" : 0,
    "prior_r" : 1,
    "prior_alpha" : 1
}

DEFAULT_HMC_OPTIONS = {
    "num_iters" : 1,
    "Tau" : 25,
    "epsilon_factor" : 0.001,
    "isPlot" : 0
}

DEFAULT_PLOTTING_OPTIONS = {
    "circle_size" : 0.1,
    "circle_alpha" : 0.15,
    "num_points" : 1000
}

NAMES_GPLVM_DPMIX_INTEGRATE_INFER_OPTIONS = DEFAULT_GPLVM_DPMIX_INTEGRATE_INFER_OPTIONS.keys()
NAMES_HMC_OPTIONS = DEFAULT_HMC_OPTIONS.keys()
NAMES_PLOTTING_OPTIONS = DEFAULT_PLOTTING_OPTIONS.keys()

# def mixture_likelihood_integrate(X, resp, prior):
    # pass

# def gplvm_likelihood(X, Y, log_hypers):
    # pass

def cholupdate(chol, something, direction_adjustment):
    pass

def gammaln(x): # appears in gaussian_dpmixture_gibbsstep
    pass

def draw_latent_representation(X, mix, assignments, labels):
    pass

def draw_gpmapping_mixgauss(X, Y, mix, kernel_log_hypers, assignments, labels, plot_options):
    pass

def fill_w_defaults(options, defaults):
    for key in defaults:
        if key not in options:
            options[key]

# def hmc(joint_likelihood_integrate, unwrapped_params, hmc_options, labels, Y, assignments, params, prior):
    # pass

# def joint_likelihood_integrate(???):
    # pass

def joint_likelihood_fixedgaussian(???):
    pass

# def sampling_dphyperparameter(alpha, N, n_components, a, b):
    # pass

def nans(shape):
    return np.empty(shape).fill(np.nan)

def mxsq(m):
    return m.T*m

# def gaussian_dpmixture_gibbsstep(X, assignments, gauss_wish_prior, dirichlet_prior, post):
    # pass

def gaussian_mixture_gibbsstep(X, assignments, gauss_wish_prior, dirichlet_prior, post):
    pass

# def gplvm_original(Y, latent_dimension, gplvm_options):
    # pass

def cholcov(matrix):
    pass

def kmeans(init_X, n_components, emptyactino, singleton):
    pass

def gplvm_dpmix_integrate_infer(latent_dimension, n_components, Y, labels, options, hmc_options, plot_options):
    N, input_dimension = Y.shape
    num_iters = NUM_ITERS

    fill_w_defaults(options, DEFAULT_GPLVM_DPMIX_INTEGRATE_INFER_OPTIONS)
    fill_w_defaults(hmc_options, DEFAULT_HMC_OPTIONS)
    fill_w_defaults(plot_options, DEFAULT_PLOTTING_OPTIONS)

    # Force latent dimension if not GP
    if options['isGP'] == 0:
        latent_dimension = input_dimension

    # Determine initializations for latent dimensions
    if latent_dimension == input_dimension:
        init_X = Y
    elif options['isGPLVMinit']:
        gplvm_options = []
        gplvm_params = gplvm_original(Y, latent_dimension, gplvm_options)
        init_X = gplvm_params.X
    elif latent_dimension < input_dimension:
        init_X = Y[:, 0:latent_dimension] # Simple truncation
    else:
        init_X[:, 0:input_dimension] = Y
        init_X[:, (input_dimension + 1):latent_dimension] = 0

    # Set up some maps for priors & posteriors
    kernel_log_hypers = {}
    gauss_wish_prior = {}
    dirichlet_prior = {}
    post = {}

    params = {'X' : init_X, 'log_hypers' : kernel_log_hypers}

    # Initialize kernel hyperparameters
    kernel_log_hypers['alpha'] = -1,
    kernel_log_hypers['betainv'] = -1
    kernel_log_hypers['gamma'] = -1

    # Set priors for Gaussian-Wishart
    gauss_wish_prior['r'] = options['prior_r']
    gauss_wish_prior['nu'] = latent_dimension
    gauss_wish_prior['S'] = np.identity(latent_dimension)
    gauss_wish_prior['m'] = np.zeros(latent_dimension)
    gauss_wish_prior['Chol'] = cholcov(gauss_wish_prior['S'])

    # Dirichlet prior
    dirichlet_prior['alpha'] = options['prior_alpha']
    dircihlet_prior['a'] = 1
    dircihlet_prior['b'] = 1

    # Track the assignments at each time t with a dictionary
    hist_assignments = []

    # Initialize assignments
    if n_components == 0:
        n_components = 1
        assignments = np.zeros( (N,1) )
        assignments[0,0] = 1
    else:
        assignments = np.zeros( (N, n_components) )
        cidx = kmeans(init_X, n_components, 'emptyaction', 'singleton')
        for z in xrange(n_components):
            assignments[cidx == z, z] = 1

    # Initialize posteriors
    post['ns'] = nans( (n_components, 1) )
    post['rs'] = nans( (n_components, 1) )
    post['nus'] = nans( (n_components, 1) )
    post['ms'] = nans( (n_components, latent_dimension) )
    post['Chols'] = nans( (latent_dimension, latent_dimension, n_components) )
    post['alphas'] = nans( (n_components, 1) )

    # NOTE - This is global in the Matlab code?
    gammaterm_n = nans( (N, 1) )

    acceptance_rate = 0
    arate_cnt = 0
    arate_start = 100

    # Initialize negative log likelihood
    nll = []

    run_hypers_alpha = []
    run_hypers_inv_beta = []
    run_hypers_gamma[]
    
    sampled_mixtures = []
    sampled_warpings = []

    for i in xrange(num_iters):

        # Calc posteriors for gaussian-wishart hypers
        # (integrate out means and covariances of latent gaussians, exactly)

        if options['isFixedGauss'] == 0:
            for z in xrange(n_components):
                post['ns'][z] = np.sum(assignments[:, z], 1) #??? how does '1' work in matlab?
                post['alpha'][z] = dirichlet_prior['alpha'] + post['ns'][z]
                post['rs'][z] = gauss_wish_prior['r'] + post['ns'][z]
                post['nus'][z] = gauss_wish_prior['nu'] + post['ns'][z]

                if post['ns'][z] > 0:
                    Xz = params['X'][assignments[:, z] == 1, :]

                    post_ms_z_num = (prior['r'] * prior['m'] + np.sum(Xz, 1))
                    post_ms_z_denom = (prior[ 'r'] + post['ns'][z])
                    post['ms'][z, :] = post_ms_z_num / post_ms_z_denom

                    S_a = gauss_wish_prior['S'] + mxsq(Xz)
                    S_b = gauss_wish_prior['r'] * mxsq(gauss_wish_prior['m'])
                    S_c = post['rs'][z] * mxsq(post['ms'][z,:])
                    S = S_a + S_b + S_c

                    post['Chols'][:,:,z] = cholcov(S)
                else:
                    post['ms'][z,:] = gauss_wish_prior['m']
                    post['Chols'][:,:,z] = cholcov(gauss_wish_prior['S'])


            # Sample cluster assignments
            if options['isDP'] == 1:
                L, assignments, post = gaussian_dpmixture_gibbsstep(params['X'], assignments, gauss_wish_prior, dirichlet_prior, post)
            else:
                L, assignments, post = gaussian_mixture_gibbsstep(params['X'], assignments, gauss_wish_prior, dirichlet_prior, post)

            # Save assignments!
            hist_assignments.append( assignments )
            Ls.append(L)
            Ks.append( numel(find(sum(assignments, 1) > 0)) ) #...wat

            if options['isSamplingDPparameter'] == 1:
                dirichlet_prior['alpha'] = sampling_dphyperparameter(dirichlet_prior['alpha'], N, n_components, dirichlet_prior['a'], dirichlet_prior['b'])

            n_components = assignments.shape[1]

        else:
            Ls.append(0)
            Ks.append(1)
            hist_assignments.append(np.nan)

        # Sample X and GP-LVM hypers given cluster assignments using HMC
        if options['isGP'] == 1:
            try:
                if options['isFixedGauss'] == 0:
                    params, nll_next, arate0 = hmc(
                            joint_likelihood_integrate, params, hmc_options, 
                            labels, Y, assignments, params, prior
                    ) # TODO
                    nll.append(nll_next)

                    if i > arate_start:
                        acceptance_rate = acceptance_rate + arate0
                        arate_cnt = arate_cnt + 1

                else:
                    params, nll_next, _ = hmc(
                            joint_likelihood_fixedgaussian, unwrapped_params, 
                            hmc_options, labels, Y, assignments, params, prior
                    ) # TODO
                    nll.append(nll_next)
            except:
                nll.append(np.nan)
                print 'R'
        else:
            nll.append(-L)

        run_hypers_alpha.append( np.exp( kernel_log_hypers['alpha'] ) )
        run_hypers_inv_beta.append( np.exp( kernel_log_hypers['betainv'] ) )
        run_hypers_gamma.append( np.exp( kernel_log_hypers['gamma'] ) )

        sampled_mixtures.append( post )
        sampled_warpings.append( params )

        # Drawing (i.e., visualization)
        if options['isMovie'] == 1:
            if options['isFixedGauss'] == 0:

                # TODO - where do I put the mix?
                mix['weights'] = post['ns'] / np.sum(post['ns']) # what is matlab ./
                mix['mus'] = post['ms']

                for z in xrange(n_components):
                    C = chol(inv(mxsq(post['Chols'][:,:,z]))) # TODO
                    mix['decomps'][:,:,z] = np.sqrt(post['nus'][z]) * C
            else:
                mix['weights'] = 1
                mix['mus'] = np.zeros( (1, latent_dimension) )
                mix['decomps'] = np.identity(latent_dimension)

            if numel(labels) > 0: # TODO what is numel?
                draw_latent_representation(params['X'], mix, assignments, labels)
                # TODO figure out how to organize the frame data and then do
                # movie_frames[i] = curframe

        if options['isPlot'] ~= 0: # TODO do I have an approx 0?
            if (mod(i, options['isPlot']) == 0) or (i == num_iters):
                if options['isFixedGauss'] == 0:

                    mix['weights'] = post['ns'] / np.sum(post['ns']) # what is matlab ./
                    mix['mus'] = post['ms']

                    for z in xrange(n_components):
                        C = chol(inv(mxsq(post['Chols'][:,:,z]))) # TODO
                        mix['decomps'][:,:,z] = np.sqrt(post['nus'][z]) * C
                else:
                    mix['weights'] = 1
                    mix['mus'] = np.zeros( (1, latent_dimension) )
                    mix['decomps'] = np.identity(latent_dimension)

                # Draw it somehow....
                # Set up plot
                if numel(labels) > 0:
                    draw_latent_representation(params['X'], mix, assignments, labels)
                else:
                    draw_latent_representation(params['X'], mix, assignments)

                if (isGP == 1) and (input_dimension == 2):
                    # Set up plot
                    draw_gpmapping_mixgauss(
                            params['X'], Y, mix, kernel_log_hypers,
                            assignments, labels, plot_options
                    )

                # Do some plotting bis....
                # Plot some hyper parametr stuff...

    # TODO is this the correct indentation
    acceptance_rate = acceptance_rate / arate_cnt
