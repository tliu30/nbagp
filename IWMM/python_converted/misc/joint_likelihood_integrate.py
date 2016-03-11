def joint_likelihood_integrate(combined_params, Y, resp, example_params_struct, prior):

    # Figure out the "rewrap"
    # cur_params = rewrap(example_params_struct, combined_params)

    nll_mix, dnll_mix = mixture_likelihood_integrate(cur_params['X'], resp, prior)

    nll_lvm, dnll_lvm_X, dnll_log_hypers =
        gplvm_likelihood(cur_params['X'], Y, cur_params['log_hypers'])

    nll_back = 0
    dnll_back_X = 0
    nll = nll_lvm + nll_mix + nll_back

    all_grads_struct = {}
    all_grads_struct['X'] = dnll_lvm_X + dnll_mix_X + dnll_back_X
    all_grads_struct['log_hypers'] = dnll_log_hypers

    # What does unwrap do?
    # dnll = unwrap(all_grads_struct)

    return (nll, dnll)
