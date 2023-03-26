import React, { useState } from 'react';
import axios from 'axios';
import { Image, Form, Button } from 'react-bootstrap';
// import { useForm } from 'react-hook-form';

function Input() {
  const [image, setImage] = useState();
  const [predictImageURL, setPredictImageURL] = useState();

  function handleImageChange(e) {
    setImage(e.target.files[0]);
  }

  async function handleSubmit(e) {
    e.preventDefault();

    // console.log(image);
    // console.log(URL.createObjectURL(image));

    const formData = new FormData();
    formData.append('image', image);

    // for (const value of formData.values()) {
    //   console.log(value);
    // }

    const response = await axios.post('/api/upload', formData);
    // console.log(response.data.url);
    setPredictImageURL(response.data.url);
  }

  return (
    <Form onSubmit={handleSubmit} encType="multipart/form-data">
      <h2>Add Image:</h2>
      <Form.Control type="file" onChange={handleImageChange} />
      <Button variant="primary" type="submit">
        Submit
      </Button>
      {image && <Image fluid src={URL.createObjectURL(image)} />}
      {predictImageURL && <Image fluid src={predictImageURL} />}
    </Form>
  );
}

export default Input;
