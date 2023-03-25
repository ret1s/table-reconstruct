import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import Input from './Input';

function Home() {
  return (
    <section>
      <Container fluid className="home-section" id="home">
        <Container fluid className="home-about-section" id="home">
          <Container fluid className="home-about-body" id="home">
            <Input />
          </Container>
        </Container>
      </Container>
    </section>
  );
}

export default Home;
