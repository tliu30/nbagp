def loglikelihood(dim, num0, r0, nu0, Chol0, num, r, nu, Chol, gammaterm_n):
    L1 = 0.5 * num * dim * np.log(np.pi)
    L2 = 0.5 * num0 * dim * np.log(np.pi)
    L3 = 0.5 * dim * np.log(r)
    L4 = 0.5 * dim * np.log(r0)
    L5 = nu * np.sum(np.log(np.diag(Chol)))
    L6 = nu0 * np.sum(np.log(np.diag(Chol0)))

    if np.isnan(gammaterm_n[num]):
        gammaterm_n[num] = 0
        for d in xrange(dim):
            a = gammaln(0.5 * (nu + 1 - d))
            b = gammaln(0.5 * (nu0 + 1 - d))

            gammaterm_n[num] += (a-b)

    L = L6 - L5 + L4 - L3 + L2 - L1 + gammaterm_n[num]

    return L # Do I also need to return gammaterm_n somehow?

def loglikelihood2(dim, num0, r0, nu0, Chol0, num, r, nu, Chol):
    L1 = 0.5 * num * dim * np.log(np.pi)
    L2 = 0.5 * num0 * dim * np.log(np.pi)
    L3 = 0.5 * dim * np.log(r)
    L4 = 0.5 * dim * np.log(r0)
    L5 = nu * np.sum(np.log(np.diag(Chol)))
    L6 = nu0 * np.sum(np.log(np.diag(Chol0)))

    gamma_part = 0
    for d in xrange(dim):
        a = gammaln(0.5 * (nu + 1 - d))
        b = gammaln(0.5 * (nu0 + 1 - d))

        gamma_part += (a-b)

    L = L6 - L5 + L4 - L3 + L2 - L1 + gamma_part

    return L

def gaussian_dpmixture_gibbsstep(X, assignments, gauss_wish_prior, dirichlet_prior, post):

    N, dim = X.shape
    n_components = assignments.shape[1]

    for n in xrange(N):
        cur_z = find(assignments[n, :]) # TODO what is the MATLAB 'find'

        assignments[n, cur_z] = 0
        if post['ns'][cur_z] == 1:
            # Delete an unassigned component
            post['Chols'][:,:,cur_z] = []
            assignments[:,cur_z] = []
            post['ms'][cur_z,:] = []
            post['ns'][cur_z] = []
            post['rs'][cur_z] = []
            post['nus'][cur_z] = []
            post['alphas'][cur_z] = []
            n_components -= 1

        else:
            # Omit the current sample
            post['Chols'][:,:,cur_z] = cholupdate(
                post['Chols'][:,:,cur_z], 
                np.sqrt(post['rs'][cur_z]) * post['ms'][cur_z,:].T,
                '+'
            )

            post['ms'][cur_z,:] = post['ms'][cur_z,:] * 
                (prior['r'] + post['ns'][cur_z]) - X[n,:]

            post['ns'][cur_z] -= 1
            post['rs'][cur_z] -= 1
            post['nus'][cur_z] -= 1
            post['ms'][cur_z,:] = post['ms'][cur_z,:] / (prior['r'] + post['ns'][cur_z])

            post['Chols'][:,:,cur_z] = cholupdate(
                post['Chols'][:,:,cur_z], X[n,:].T, '-'
            )

            post['Chols'][:,:,cur_z] = cholupdate(
                post['Chols'][:,:,cur_z],
                sqrt(post['rs'][cur_z]) * post['ms'][cur_z,:].T,
                '-'
            )

            post['alphas'][cur_z] -= 1

        # Dirichlet-multinomial part
        prob = [np.log(np.sum(assignments,1)), np.log(dirichlet_prior['alpha'])] # TODO sum dimension

        # Gaussian-Wishart part
        for z in xrange(n_components):
            Chol = cholupdate(post['Chols'][:,:,z], sqrt(post['rs'][z]) * post['ms'][z,:].T, '+')
            m = post['ms'][z,:] * (prior['r'] + post['ns'][z]) + X[n,:]
            num = post['ns'][z] + 1
            r = post['rs'][z] + 1
            nu = post['nus'][z] + 1
            m = m / (prior['r'] + num)
            Chol = cholupdate(Chol, X[n,:].T, '+')
            Chol = cholupdate(Chol, np.sqrt(r)*m.T, '-')

            prob[z] = prob[z] + loglikelihood(
                dim, post['ns'][z], post['rs'][z], post['nus'][z], 
                post['Chols'][:,:,z], num, r, nu, Chol
            )

        newm = prior['r'] * prior['m'] + X[n,:] / (prior['r'] + 1)
        newr = prior['r'] + 1
        newnu = prior['nu'] + 1
        newS = prior['S'] + mxsq(X[n,:]) + prior['r'] * mxsq(prior['m']) - newr * mxsq(newm)
        newChol = cholcov(newS)
        prob[-1] = prob[-1] + loglikelihood(dim, 0, prior['r'], prior['nu'], prior['chol'],
                1, newr, newnu, newChol) # unclear if should be an append or a -1 index...

        # Normalize probabilities
        psum = sp.misc.logsumexp(prob, 1) # need to make sure have write axis...
        prob = np.exp(prob - psum)

        # Sampling assignment
        newassignment = mnrnd(1, [prob[:-1], 1 - np.sum(prob[:-1])]) # multinomial rand
        if np.isnan(newassignment):
            newassignment = np.zeros(1, n_components + 1)
            maxind = np.argmax(prob)
            newassignment[maxind] = 1
        cur_Z = find(newassignment)

        if newassignment[-1] == 1:
            # Initialize posteriors
            assignments = [assignments, zeros(N,1)] # check this step
            assignments[n, cur_z] = 1
            post['ns'][cur_z] = 1
            post['rs'][cur_z] = gaus_wish_prior['r'] + 1
            post['nus'][cur_z] = gaus_wish_prior['nu'] + 1
            post['ms'][cur_z] = (gaus_wish_prior['r'] * gaus_wish_prior['m'] + X[n,:]) /
                (gaus_wish_prior['r'] + 1)
            S = gaus_wish_prior['S'].T * X[n,:] + gaus_wish_prior['r'] * mxsq(gaus_wish_prior['m']) -
                post['rs'][cur_z] * mxsq(post['ms'][cur_z,:])
            post['Chols'][:,:,cur_z] = cholcov(S)
            post['alphas'][cur_z] = prior['alpha'] + 1
            n_components = n_components + 1
        else:
            # Update hyperparams by sampled assignment
            assignments[n,cur_z] = 1;
            post['Chols'][:,:,cur_z] = cholupdate(
                post['Chols'][:,:,cur_z], 
                sqrt(post['rs'][cur_z] * post['ms'][cur_z,:].T,
                '+'
            )
            post['ms'][cur_z,:] = 
                post['ms'][cur_z,:] * (prior['r'] + post['ns'][cur_z]) + X[n,:]
            post['ns'][cur_z] = post['ns'][cur_z] + 1;
            post['rs'][cur_z] = post['rs'][cur_z] + 1;
            post['nus'][cur_z] = post['nus'][cur_z] + 1;
            post['ms'][cur_z,:] = post['ms'][cur_z,:] / (prior['r'] + post['ns'][cur_z]);
            post['Chols'][:,:,cur_z] = cholupdate(
                post['Chols'][:,:,cur_z], X[n,:].T, '+'
            );
            post['Chols'][:,:,cur_z] = cholupdate(
                post['Chols'][:,:,cur_z], np.sqrt(post['rs'][cur_z]] * post.ms[cur_z,:].T), '-'
            )
            post['alphas'][cur_z] = post['alphas'][cur_z];

    return (L, assignments, post)
