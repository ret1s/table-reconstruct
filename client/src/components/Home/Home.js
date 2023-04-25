import React from 'react';
import { Container } from '@chakra-ui/react';
import Input from './Input';
import HeadPage from './HeadPage';

function Home() {
  return (
    <section>
      <Container maxW="95%" className="head-page">
        <HeadPage />
      </Container>
      <Container maxW="88%" minH="90%" bg="#e0f2f1" className="home-section">
        <Container maxW="100%" className="home-content">
          <Input />
        </Container>
      </Container>
    </section>
  );
}

export default Home;

