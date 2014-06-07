from django.db import models
from django.core.signals import Signal
from observer.tests.compat import TestCase
from observer.tests.compat import MagicMock
from observer.utils.signals import (register_reciever,
                                    unregister_reciever)


class ObserverUtilsSignalsRegisterReceiverTestCase(TestCase):
    def setUp(self):
        self.model = MagicMock(wraps=models.Model)
        self.signal = MagicMock(wraps=Signal,
                                **{'connect.return_value': None})
        self.receiver = MagicMock()

    def test_register_reciever_call_connect(self):
        """should call connect to connect signal and receiver"""
        register_reciever(self.model,
                          self.signal,
                          self.receiver)
        # signal.connect should be called with receiver and model
        self.signal.connect.assert_called_with(
            self.receiver, sender=self.model, weak=False)

    def test_register_reciever_call_connect_once(self):
        """should call connect only once to prevent the duplication"""
        for i in range(5):
            register_reciever(self.model,
                              self.signal,
                              self.receiver)
        # signal.connect should be called once
        self.signal.connect.assert_called_once_with(
            self.receiver, sender=self.model, weak=False)

    def test_register_reciever_return_true_for_1st(self):
        """should return True for the 1st call"""
        r = register_reciever(self.model,
                              self.signal,
                              self.receiver)
        self.assertTrue(r)

    def test_register_reciever_return_false_for_2nd(self):
        """should return False for the 2nd and further call"""
        register_reciever(self.model,
                          self.signal,
                          self.receiver)
        # 2nd call
        r = register_reciever(self.model,
                              self.signal,
                              self.receiver)
        self.assertFalse(r)
        # 3rd call
        r = register_reciever(self.model,
                              self.signal,
                              self.receiver)
        self.assertFalse(r)

    def test_register_reciever_call_connect_of_individual_signals(self):
        """should call connect when signals are different"""
        signals = [MagicMock(wraps=Signal, **{'connect.return_value': None})
                   for i in range(5)]
        for signal in signals:
            register_reciever(self.model,
                              signal,
                              self.receiver)
            signal.connect.assert_called_once_with(
                self.receiver, sender=self.model, weak=False)

    def test_register_reciever_call_connect_of_individual_receivers(self):
        """should call connect when receivers are different"""
        receivers = [MagicMock() for i in range(5)]
        for receiver in receivers:
            register_reciever(self.model,
                              self.signal,
                              receiver)
            self.signal.connect.assert_called_with(receiver, weak=False,
                                                   sender=self.model)
        # called multiple times
        self.assertEqual(self.signal.connect.call_count, 5)

    def test_register_reciever_prefer_specified_sender(self):
        """should call connect with specified sender"""
        sender = MagicMock()
        register_reciever(self.model,
                          self.signal,
                          self.receiver,
                          sender=sender)
        # signal.connect should be called once with specified sender
        self.signal.connect.assert_called_once_with(
            self.receiver, sender=sender, weak=False)

    def test_register_reciever_pass_the_options(self):
        """should call connect with specified **kwargs"""
        register_reciever(self.model,
                          self.signal,
                          self.receiver,
                          weak=True,
                          foo='bar')
        # signal.connect should be called once with specified **kwargs
        # but weak cannot be modified
        self.signal.connect.assert_called_once_with(
            self.receiver, sender=self.model,
            weak=False, foo='bar',
        )


class ObserverUtilsSignalsUnregisterReceiverTestCase(TestCase):
    def setUp(self):
        self.model = MagicMock(wraps=models.Model)
        self.signal = MagicMock(wraps=Signal, **{
            'connect.return_value': None,
            'disconnect.return_value': None,
        })
        self.receiver = MagicMock()
        register_reciever(self.model,
                          self.signal,
                          self.receiver)

    def test_unregister_reciever_call_disconnect(self):
        """should call disconnect to disconnect signal and receiver"""
        unregister_reciever(self.model,
                            self.signal,
                            self.receiver)
        # signal.connect should be called with receiver and model
        self.signal.disconnect.assert_called_with(
            self.receiver)

    def test_unregister_reciever_call_disconnect_once(self):
        """should call disconnect only once to prevent the exception"""
        for i in range(5):
            unregister_reciever(self.model,
                                self.signal,
                                self.receiver)
        # signal.connect should be called once
        self.signal.disconnect.assert_called_once_with(
            self.receiver)

    def test_unregister_reciever_return_true_for_1st(self):
        """should return True for the 1st call"""
        r = unregister_reciever(self.model,
                                self.signal,
                                self.receiver)
        self.assertTrue(r)

    def test_unregister_reciever_return_false_for_2nd(self):
        """should return False for the 2nd and further call"""
        unregister_reciever(self.model,
                            self.signal,
                            self.receiver)
        # 2nd call
        r = unregister_reciever(self.model,
                                self.signal,
                                self.receiver)
        self.assertFalse(r)
        # 3rd call
        r = unregister_reciever(self.model,
                                self.signal,
                                self.receiver)
        self.assertFalse(r)

    def test_unregister_reciever_call_disconnect_of_individual_signals(self):
        """should call connect when signals are different"""
        prop = {
            'connect.return_value': None,
            'disconnect.return_value': None,
        }
        signals = [MagicMock(wraps=Signal, **prop)
                   for i in range(5)]
        for signal in signals:
            register_reciever(self.model,
                              signal,
                              self.receiver)
        for signal in signals:
            unregister_reciever(self.model,
                                signal,
                                self.receiver)
            signal.disconnect.assert_called_once_with(self.receiver)

    def test_unregister_reciever_call_connect_of_individual_receivers(self):
        """should call connect when receivers are different"""
        receivers = [MagicMock() for i in range(5)]
        for receiver in receivers:
            register_reciever(self.model,
                              self.signal,
                              receiver)
        for receiver in receivers:
            unregister_reciever(self.model,
                                self.signal,
                                receiver)
            self.signal.disconnect.assert_called_with(receiver)
        # called multiple times
        self.assertEqual(self.signal.disconnect.call_count, 5)
