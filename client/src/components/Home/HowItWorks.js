import { ReactElement } from 'react';
import { Box, SimpleGrid, Icon, Text, Stack, Flex } from '@chakra-ui/react';
import { FcUpload, FcDocument, FcDownload } from 'react-icons/fc';

interface FeatureProps {
    title: string;
    text: string;
    icon: ReactElement;
}

const Feature = ({ title, text, icon }: FeatureProps) => {
    return (
        <Stack alignItems={'flex-start'}>
            <Flex
                w={16}
                h={16}
                align={'center'}
                justify={'center'}
                color={'white'}
                rounded={'full'}
                bg={'gray.100'}
                mb={1}>
                {icon}
            </Flex>
            <Text fontWeight={600}>{title}</Text>
            <Text align={"justify"} color={'gray.600'}>{text}</Text>
        </Stack>
    );
};

export default function SimpleThreeColumns() {
  return (
    <Box p={4}>
        <Text fontSize='4xl' fontFamily={'Lora-Regular'}>How It Works?</Text>
        <br></br>
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={10}>
            <Feature
                icon={<Icon as={FcUpload} w={10} h={10} />}
                title={'Upload your file'}
                text={
                    'Click "Choose File" and select file from your local machine. Your file will be uploaded safely over an encrypted connection.'
                }
            />
            <Feature
                icon={<Icon as={FcDocument} w={10} h={10} />}
                title={'Edit & Review'}
                text={
                    'The document will be processed. Once it finished, you can see the extracted tables and can fix them right there if find any issues.'
                }
            />
            <Feature
                icon={<Icon as={FcDownload} w={10} h={10} />}
                title={'Convert & Download'}
                text={
                    'The extracted tables can be converted into Excel/CSV/PDF format. Choose the right format in "File->Save as.." to download it to your local machine.'
                }
            />
        </SimpleGrid>
    </Box>
  );
}