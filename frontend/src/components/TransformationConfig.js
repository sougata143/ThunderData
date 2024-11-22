import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';

const TRANSFORMATION_TYPES = {
  tokenization: {
    name: 'Tokenization',
    description: 'Split text into individual tokens',
    params: ['columns']
  },
  stopword_removal: {
    name: 'Stopword Removal',
    description: 'Remove common stopwords',
    params: ['columns', 'language']
  },
  lemmatization: {
    name: 'Lemmatization',
    description: 'Reduce words to their base form',
    params: ['columns']
  },
  text_vectorization: {
    name: 'Text Vectorization',
    description: 'Convert text to numerical features',
    params: ['columns', 'method', 'max_features', 'ngram_range']
  },
  named_entity_recognition: {
    name: 'Named Entity Recognition',
    description: 'Extract named entities from text',
    params: ['columns', 'entity_types']
  },
  pos_tagging: {
    name: 'Part of Speech Tagging',
    description: 'Tag words with their parts of speech',
    params: ['columns']
  },
  stemming: {
    name: 'Stemming',
    description: 'Reduce words to their root/stem form',
    params: ['columns']
  }
};

function TransformationConfig({ config, onConfigUpdate }) {
  const [newTransform, setNewTransform] = useState({
    type: '',
    columns: '',
    language: 'english',
    method: 'tfidf',
    max_features: 1000,
    ngram_range: [1, 2],
    entity_types: ['PERSON', 'ORG', 'GPE']
  });
  const [inputColumn, setInputColumn] = useState('');

  const handleAddTransformation = () => {
    if (!newTransform.type || !newTransform.columns) return;

    const transformConfig = {
      type: newTransform.type,
      params: {
        columns: newTransform.columns.split(',').map(c => c.trim())
      }
    };

    // Add additional parameters based on transformation type
    if (newTransform.type === 'stopword_removal') {
      transformConfig.params.language = newTransform.language;
    } else if (newTransform.type === 'text_vectorization') {
      transformConfig.params.method = newTransform.method;
      transformConfig.params.max_features = newTransform.max_features;
      transformConfig.params.ngram_range = newTransform.ngram_range;
    } else if (newTransform.type === 'named_entity_recognition') {
      transformConfig.params.entity_types = newTransform.entity_types;
    }

    onConfigUpdate({
      ...config,
      transformations: [...config.transformations, transformConfig]
    });

    // Reset form
    setNewTransform({
      type: '',
      columns: '',
      language: 'english',
      method: 'tfidf',
      max_features: 1000,
      ngram_range: [1, 2],
      entity_types: ['PERSON', 'ORG', 'GPE']
    });
  };

  const handleRemoveTransformation = (index) => {
    const newTransformations = config.transformations.filter((_, i) => i !== index);
    onConfigUpdate({ ...config, transformations: newTransformations });
  };

  const handleInputColumnChange = (e) => {
    const newInputColumn = e.target.value;
    setInputColumn(newInputColumn);
    onConfigUpdate({
      ...config,
      input_column: newInputColumn
    });
  };

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 3 }}>
        Configure Text Transformations
      </Typography>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 3 }}>
            <TextField
              fullWidth
              label="Input Column Name"
              value={inputColumn}
              onChange={handleInputColumnChange}
              helperText="Enter the name of the column containing text to process"
            />

            <FormControl fullWidth>
              <InputLabel>Transformation Type</InputLabel>
              <Select
                value={newTransform.type}
                label="Transformation Type"
                onChange={(e) => setNewTransform({ ...newTransform, type: e.target.value })}
              >
                {Object.entries(TRANSFORMATION_TYPES).map(([key, value]) => (
                  <MenuItem key={key} value={key}>
                    {value.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Columns (comma-separated)"
              value={newTransform.columns}
              onChange={(e) => setNewTransform({ ...newTransform, columns: e.target.value })}
            />

            {newTransform.type === 'stopword_removal' && (
              <FormControl fullWidth>
                <InputLabel>Language</InputLabel>
                <Select
                  value={newTransform.language}
                  label="Language"
                  onChange={(e) => setNewTransform({ ...newTransform, language: e.target.value })}
                >
                  <MenuItem value="english">English</MenuItem>
                  <MenuItem value="spanish">Spanish</MenuItem>
                  <MenuItem value="french">French</MenuItem>
                </Select>
              </FormControl>
            )}

            {newTransform.type === 'text_vectorization' && (
              <Box sx={{ display: 'flex', gap: 2 }}>
                <FormControl fullWidth>
                  <InputLabel>Method</InputLabel>
                  <Select
                    value={newTransform.method}
                    label="Method"
                    onChange={(e) => setNewTransform({ ...newTransform, method: e.target.value })}
                  >
                    <MenuItem value="tfidf">TF-IDF</MenuItem>
                    <MenuItem value="count">Count Vectorizer</MenuItem>
                  </Select>
                </FormControl>

                <TextField
                  fullWidth
                  type="number"
                  label="Max Features"
                  value={newTransform.max_features}
                  onChange={(e) => setNewTransform({ ...newTransform, max_features: parseInt(e.target.value) })}
                />
              </Box>
            )}

            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleAddTransformation}
              disabled={!newTransform.type || !newTransform.columns}
            >
              Add Transformation
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Typography variant="subtitle1" sx={{ mb: 2 }}>
        Configured Transformations:
      </Typography>

      <List>
        {config.transformations.map((transform, index) => (
          <ListItem key={index}>
            <ListItemText
              primary={TRANSFORMATION_TYPES[transform.type].name}
              secondary={`Columns: ${transform.params.columns.join(', ')}`}
            />
            <ListItemSecondaryAction>
              <IconButton
                edge="end"
                aria-label="delete"
                onClick={() => handleRemoveTransformation(index)}
              >
                <DeleteIcon />
              </IconButton>
            </ListItemSecondaryAction>
          </ListItem>
        ))}
      </List>

      {config.transformations.length === 0 && (
        <Typography color="textSecondary" align="center">
          No transformations configured yet
        </Typography>
      )}
    </Box>
  );
}

export default TransformationConfig;
