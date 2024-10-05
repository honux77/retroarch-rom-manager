class TestDecorator:

    def setup_method(self):
        import config
        self.config = config.Config()

    def test_singleton(self):
        '''
        싱글톤 테스트
        '''
        import config
        config1 = config.Config()
        config2 = config.Config()
        assert config1 == config2
        assert config1 is config2