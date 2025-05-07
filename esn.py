import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import MinMaxScaler

class Reservoir:
    def __init__(self, n_reservoir, n_inputs, spectral_radius=0.9, sparsity=0.1, leaking_rate=0.6):
        self.n_reservoir = n_reservoir
        self.n_inputs = n_inputs
        self.leaking_rate = leaking_rate

        self.W_in = np.random.uniform(-1, 1, (n_reservoir, n_inputs + 1))
        self.W = np.random.uniform(-1, 1, (n_reservoir, n_reservoir))
        mask = np.random.rand(*self.W.shape) > sparsity
        self.W[mask] = 0
        eigvals = np.linalg.eigvals(self.W)
        self.W *= spectral_radius / np.max(np.abs(eigvals))

        self.state = np.zeros((n_reservoir, 1))

    def update_state(self, input_vector):
        input_vector_with_bias = np.vstack((np.array([[1]]), input_vector))
        pre_activation = np.dot(self.W, self.state) + np.dot(self.W_in, input_vector_with_bias)
        updated = np.tanh(pre_activation)
        self.state = (1 - self.leaking_rate) * self.state + self.leaking_rate * updated
        return self.state.flatten()

class EchoStateNetwork:
    def __init__(self, n_inputs, n_reservoir, n_outputs,
                 spectral_radius=0.9, sparsity=0.3, leaking_rate=0.6):
        self.n_inputs = n_inputs
        self.n_reservoir = n_reservoir
        self.n_outputs = n_outputs
        self.reservoir = Reservoir(n_reservoir, n_inputs, spectral_radius, sparsity, leaking_rate)

        self.scaler_input = MinMaxScaler(feature_range=(-1, 1))
        self.scaler_output = MinMaxScaler(feature_range=(-1, 1))

        self.W_out = None
        self.W_out_bias = None

    def fit(self, inputs, outputs, reg=1e-5):
        inputs_scaled = self.scaler_input.fit_transform(inputs)
        outputs_scaled = self.scaler_output.fit_transform(outputs)

        states = []
        for input_vector in inputs_scaled:
            state = self.reservoir.update_state(input_vector.reshape(-1, 1))
            states.append(state)
        states = np.array(states)

        states_with_bias = np.hstack((np.ones((states.shape[0], 1)), states))
        ridge = Ridge(alpha=reg)
        ridge.fit(states_with_bias, outputs_scaled)
        self.W_out = ridge.coef_
        self.W_out_bias = ridge.intercept_


    def predict(self, input_vector):
        """Предсказывает 1 шаг по текущему входу"""
        input_scaled = self.scaler_input.transform([input_vector])[0]
        state = self.reservoir.update_state(input_scaled.reshape(-1, 1))
        state_with_bias = np.concatenate([[1], state])
        prediction_scaled = np.dot(self.W_out, state_with_bias) + self.W_out_bias
        prediction = self.scaler_output.inverse_transform([prediction_scaled])[0]
        return prediction
