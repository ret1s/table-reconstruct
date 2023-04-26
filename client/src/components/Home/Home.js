import React from 'react';
<<<<<<< HEAD
import { Container } from '@chakra-ui/react';
import Input from './Input';
import HeadPage from './HeadPage';
import HowItWorks from './HowItWorks';
=======
import { Container } from '@chakra-ui/react'
import Input from './Input';
>>>>>>> main

function Home() {
  return (
    <section>
<<<<<<< HEAD
      <Container maxW="95%" className="head-page">
        <HeadPage />
      </Container>
      <Container maxW="88%" minH="90%" bg="#e0f2f1" className="home-section">
        <Container maxW="100%" className="home-content">
=======
      <Container maxW='95%' className="home-section">
        <Container maxW='95%' className="home-content">
>>>>>>> main
          <Input />
        </Container>
      </Container>
      <Container maxW="75%" className="how-it-works">
        <HowItWorks />
      </Container>
    </section>
  );
}

export default Home;

