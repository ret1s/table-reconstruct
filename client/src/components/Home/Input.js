import React, { useState } from 'react';
import axios from 'axios';
import { 
  Button, 
  Grid, 
  GridItem,
  FormControl,
  FormLabel,
  Input,
  Center,
  Image
} from '@chakra-ui/react';

function InputSection() {
  const [image, setImage] = useState();
  const [predictImageURL, setPredictImageURL] = useState();

  function handleImageChange(e) {
    console.log(e.target.files[0]);
    setImage(e.target.files[0]);
  }

  async function handleSubmit(e) {
    e.preventDefault();

    console.log(image);
    console.log(URL.createObjectURL(image));

    const formData = new FormData();
    formData.append('image', image);

    for (const value of formData.values()) {
      console.log(value);
    }

    const response = await axios.post('/api/upload', formData);
    console.log(response.data.url);
    setPredictImageURL(response.data.url);
  }

  return (
    <section>
      <Grid
        mt='-100px'
        mb='-200px'
        h='500px'
        templateColumns='repeat(9, 1fr)'
        gap={4}
      >
        <GridItem borderRadius='lg' borderWidth='1px' h='145px' w='270px' bg='white'>
        <form onSubmit={handleSubmit} onChange={handleImageChange}>
          <FormControl >
            <Center>
              <FormLabel fontWeight={1000} mt='10px'>Upload Image</FormLabel>
            </Center>
            <Center>
              <Input maxW='250px' type='file' accept="image/*"/>
            </Center>
            
          </FormControl>
          <Center>
              <Button type='submit' colorScheme='teal' variant='solid' mt='10px'> 
                Submit
              </Button>
            </Center>
          </form>
        </GridItem>
        <GridItem colSpan={4} bg='white' orderRadius='lg' borderWidth='1px'> 
          <Center fontSize="25" fontWeight={1000} mt='10px'>
            Input Image
          </Center>
          <Center>
           {image && <Image boxSize='90%' src={URL.createObjectURL(image)} />} 
          </Center>
        </GridItem>
        <GridItem colSpan={4} bg='white' orderRadius='lg' borderWidth='1px'> 
        <Center fontSize="25" fontWeight={1000} mt='10px'>
            Predict Cells
          </Center>
          <Center>
            {predictImageURL && <Image boxSize='90%' src={predictImageURL} />}
          </Center>
        </GridItem>
      </Grid>
    </section>
  );
}

export default InputSection;
