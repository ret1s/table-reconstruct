import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import Input from './Input';

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
