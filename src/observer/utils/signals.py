REGISTRATION_CACHE_NAME = '_observer_receivers'


def register_reciever(model, signal, receiver, sender=None, **kwargs):
    """
    Connect signal and receiver of the model without duplication

    Args:
        model (class): A target class
        signal (signal): A django signal
        receiver (reciever): A django signal receiver
        sender (model): A model class
        **kwargs: Options passed to the signal.connect method

    Returns:
        bool: True for new registration, False for already registered.
    """
    # create cache field if it does not exists
    if not hasattr(model, REGISTRATION_CACHE_NAME):
        setattr(model, REGISTRATION_CACHE_NAME, set())
    # check if the combination of signal and receiver has already registered
    # to the model, to prevent duplicate registration
    natural_key = (id(signal), id(receiver))
    receivers = getattr(model, REGISTRATION_CACHE_NAME)
    if natural_key in receivers:
        # the receiver has already registered to the model thus just ignore it
        # and return False
        return False
    # connect signal and receiver
    kwargs['weak'] = False
    signal.connect(receiver, sender=sender or model, **kwargs)
    # memorize this registration and return True
    receivers.add(natural_key)
    return True


def unregister_reciever(model, signal, receiver):
    """
    Disconnect signal and receiver of the model without exception

    Args:
        model (class): A target class
        signal (signal): A django signal
        receiver (reciever): A django signal receiver

    Returns:
        bool: True for success, False for already disconnected.
    """
    # check if the combination of signal and receiver has registered to the
    # model or not yet
    natural_key = (id(signal), id(receiver))
    receivers = getattr(model, REGISTRATION_CACHE_NAME)
    if natural_key not in receivers:
        # the receiver has not registered to the model yet thus just ignore it
        # and return False
        return False
    # disconnect signal and receiver
    signal.disconnect(receiver)
    # forget this receiver and return True
    receivers.remove(natural_key)
    return True
