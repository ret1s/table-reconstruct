import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import Input from './Input';
import { Button, ButtonGroup } from '@chakra-ui/react';

function Home() {
  return (
    <section>
      <Container fluid className="home-section" id="home">
        <Container fluid className="home-content">
          <Input />
        </Container>
      </Container>
    </section>
  );
}

export default Home;
