import {
  ChakraProvider,
  Heading,
  Container,
  Text,
  Button,
  Wrap,
  Stack, 
  Image,
  SkeletonCircle,
  SkeletonText,
} from "@chakra-ui/react";
import axios from "axios";
import { useState } from "react";

const App = () => {
  const [image, updateImage] = useState();
  const [loading, updateLoading] = useState();
  const [loadingImg, updateLoadingImg] = useState();
  const [lstImg, updateLstImg] = useState();

  const generate = async () => {
    updateLoading(true);
    const result = await axios.get(`http://127.0.0.1:8000/generate/`);
    updateImage(result.data);
    updateLoading(false);
  };

  const addToPlayer = async (player) => {
    updateLoading(true);
    await axios.post('http://127.0.0.1:8000/addToPlayer/', {
      player: player,
      img: image
    });
    updateLoading(false);
  };

  const getListPersonnages = async (player) => {
      try {
        updateLoadingImg(true);
        const result = await axios.get(`http://127.0.0.1:8000/getListPersonnages/${player}`);
        updateLstImg(result.data);
      } catch (error) {
        console.error(`Erreur lors de la récupération de la liste des personnages pour le joueur ${player} :`, error);
      } finally {
        updateLoadingImg(false);
      }
    };


  const player = "IRPYC";

  return (
    <ChakraProvider>
      <Container>
        <Heading>⚔ CardsGameAi ⚔</Heading>
        <Text marginBottom={"10px"}>
          Ouvre tes coffres et découvre ton nouveau personnage !
        </Text>

        <Wrap marginBottom={"10px"} marginTop={"10em"}>
          <Button onClick={(e) => generate()} colorScheme={"yellow"} >
            Ouvrir
          </Button>
        </Wrap>

        {loading ? (
          <Stack>
            <SkeletonCircle />
            <SkeletonText />
          </Stack>
        ) : image ? (
          <Image src={`data:image/png;base64,${image}`} boxShadow="lg" />
        ) : null}
        <Button onClick={(e) => addToPlayer(player,image)} colorScheme={"yellow"} >
            Recruter 📜
        </Button>
        <Button onClick={(j) => getListPersonnages(player)} colorScheme={"yellow"} >
            Voir la liste 📜
        </Button>
        {loadingImg ? (
          <Stack>
            <SkeletonCircle />
            <SkeletonText />
          </Stack>
        ) : lstImg ? (
          <Image src={`data:image/png;base64,${lstImg}`} boxShadow="lg" />
        ) : null}
        
      </Container>
    </ChakraProvider>
  );

};

export default App;
