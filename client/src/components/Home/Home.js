import React from 'react';
import { Container } from '@chakra-ui/react'
import Input from './Input';

function Home() {
  return (
    <section>
      <Container maxW='95%' className="home-section">
        <Container maxW='95%' className="home-content">
          <Input />
        </Container>
      </Container>
    </section>
  );
}

export default Home;