import numpy as np

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

        self.state = np.zeros((n_reservoir, 1)) * 0.01

    def update_state(self, input_vector):
        """Обновление состояния резервуара"""
        input_vector_with_bias = np.vstack((np.array([[1]]), input_vector))
        pre_activation = np.dot(self.W, self.state) + np.dot(self.W_in, input_vector_with_bias)
        updated = np.tanh(pre_activation)
        self.state = (1 - self.leaking_rate) * self.state + self.leaking_rate * updated
        return self.state.flatten()


class EchoStateNetwork:
    def __init__(self, n_inputs, n_reservoir, n_outputs, spectral_radius=0.9, sparsity=0.3, leaking_rate=0.6):
        self.n_inputs = n_inputs
        self.n_reservoir = n_reservoir
        self.n_outputs = n_outputs
        self.reservoir = Reservoir(n_reservoir, n_inputs, spectral_radius, sparsity, leaking_rate)
        self.W_out = np.random.randn(n_outputs, n_reservoir + 1) * 0.1
        self.max_vel = 200.0 # Максимальная скорость для нормализации
        self.last_distance_to_target = 0


    def reward_function(self, input_vector):
        """Функция награды"""
        pos = np.array(input_vector[0:2])
        target = np.array(input_vector[2:4])
        vel = np.array(input_vector[4:6])
        nearest = np.array(input_vector[6:8])

        current_distance = np.linalg.norm(pos - target)
        delta = 0

        self.last_distance_to_target = current_distance

        if self.last_distance_to_target is not None:
            delta = self.last_distance_to_target - current_distance

        reward = 0

        # Штраф за расстояние
        reward += delta * 100  # поощрение за приближение
        reward -= 0.01 * current_distance  # штраф за удаленность

        # Штраф за близость к препятствию
        distance_to_obstacle = np.linalg.norm(pos - nearest)
        if distance_to_obstacle < 10:
            reward -= (10 - distance_to_obstacle) * 0.5

        # Бонус за достижение цели
        if current_distance < 5:
            reward += 500
            if np.linalg.norm(vel) > 10:
                reward -= 30  # штраф за высокую скорость у цели

        robot_velocity = np.linalg.norm([vel[0], vel[1]])
        reward += robot_velocity * 10  # Поощрение за движение

      #  return np.clip(reward, -10, 10)
        return reward


    def predict(self, input_vector):
        """Предсказание с обработкой столкновений"""
    
        state = self.reservoir.update_state(input_vector.reshape(-1, 1))
        state_with_bias = np.concatenate([[1], state])
        
        prediction = np.dot(self.W_out, state_with_bias)

        if np.linalg.norm(prediction) > 1:
            prediction = prediction / np.linalg.norm(prediction)

        direction = np.array([
            input_vector[2] - input_vector[0],  
            input_vector[3] - input_vector[1]
        ])

        direction = direction / (np.linalg.norm(direction) + 1e-6)

        error = prediction - direction
        reward = self.reward_function(input_vector)

        lr = 0.1
        gradient = 2 * error[:, np.newaxis] * state_with_bias
        self.W_out -= lr * reward * gradient

        return prediction * self.max_vel
        