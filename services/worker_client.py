"""
Client for communicating with the Worker Agent.
"""
import requests
import json
from typing import Dict, Any, Optional

try:
    from config import Config
    from utils.logger import logger
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import Config
    from utils.logger import logger

class WorkerClient:
    """Client for Worker Agent API communication."""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or Config.WORKER_AGENT_URL
        self.timeout = Config.WORKER_AGENT_TIMEOUT
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make HTTP request to worker agent."""
        url = f"{self.base_url}{endpoint}"
        
        # Log request payload if present
        if 'json' in kwargs:
            try:
                payload_str = json.dumps(kwargs['json'], indent=2)
                logger.info(f'\n{"="*80}\nREQUEST PAYLOAD ({method} {endpoint}):\n{"="*80}\n{payload_str}\n{"="*80}')
            except Exception:
                logger.info(f'REQUEST PAYLOAD ({method} {endpoint}): {kwargs.get("json")}')
        
        try:
            response = requests.request(
                method,
                url,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            result = response.json()
            
            # Log response payload
            try:
                result_str = json.dumps(result, indent=2)
                logger.info(f'\n{"="*80}\nRESPONSE PAYLOAD ({method} {endpoint}):\n{"="*80}\n{result_str}\n{"="*80}')
            except Exception:
                logger.info(f'RESPONSE PAYLOAD ({method} {endpoint}): {result}')
            
            return result
        except requests.exceptions.Timeout:
            logger.error(f'Worker agent timeout: {endpoint}')
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f'Worker agent connection error: {endpoint}')
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f'Worker agent HTTP error: {e.response.status_code} - {endpoint}')
            try:
                error_body = e.response.json()
                error_str = json.dumps(error_body, indent=2)
                logger.error(f'Error response: {error_str}')
            except:
                logger.error(f'Error response: {e.response.text}')
            return None
        except Exception as e:
            logger.error(f'Worker agent request error: {str(e)} - {endpoint}')
            return None
    
    def register_worker(self) -> Optional[Dict[str, Any]]:
        """Register with worker agent."""
        return self._make_request('POST', '/register')
    
    def check_health(self) -> Optional[Dict[str, Any]]:
        """Check worker agent health."""
        return self._make_request('GET', '/health')
    
    def send_task(self, user_id: str, profile: Dict[str, Any], 
                  sleep_sessions: list = None) -> Optional[Dict[str, Any]]:
        """
        Send analysis task to worker agent.
        
        Note: The backend worker agent will automatically fetch all existing
        STM/LTM data for the user_id from its storage. Only send new sleep_sessions
        that need to be added. If sleep_sessions is None or empty, the backend will
        use only its stored data.
        
        Args:
            user_id: User identifier
            profile: User profile data
            sleep_sessions: Optional list of NEW sleep sessions to add.
                          Backend will fetch existing sessions from its storage.
        
        Returns:
            Task result or None on error
        """
        import uuid
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        # sleep_sessions is optional - backend will fetch existing data
        if sleep_sessions is None:
            sleep_sessions = []
        
        payload = {
            'task_id': task_id,
            'user_id': user_id,
            'payload': {
                'sleep_sessions': sleep_sessions,  # Only new sessions
                'profile': profile
            }
        }
        
        logger.info(f'\n{"="*80}\nSENDING TASK TO WORKER AGENT\n{"="*80}')
        logger.info(f'Task ID: {task_id}')
        logger.info(f'User ID: {user_id}')
        logger.info(f'New Sessions Count: {len(sleep_sessions)}')
        logger.info(f'Backend will automatically fetch existing STM/LTM data for this user.')
        
        result = self._make_request('POST', '/task', json=payload)
        
        if result and result.get('status') == 'completed':
            logger.info(f'\n{"="*80}\nTASK COMPLETED SUCCESSFULLY\n{"="*80}')
            logger.info(f'Task ID: {task_id}')
        elif result and result.get('status') == 'error':
            logger.error(f'\n{"="*80}\nTASK FAILED\n{"="*80}')
            logger.error(f'Task ID: {task_id}')
            logger.error(f'Error: {result.get("error")}')
        
        return result
    
    def get_memory(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user memory from worker agent.
        
        Args:
            user_id: User identifier
        
        Returns:
            Memory data or None on error
        """
        logger.info(f'\n{"="*80}\nFETCHING MEMORY FROM WORKER AGENT\n{"="*80}')
        logger.info(f'User ID: {user_id}')
        return self._make_request('GET', f'/memory?user_id={user_id}')
    
    def get_recommendations(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get recommendations for user.
        This is a convenience method that gets memory and extracts recommendations.
        
        Args:
            user_id: User identifier
        
        Returns:
            Recommendations data or None on error
        """
        logger.info(f'\n{"="*80}\nFETCHING RECOMMENDATIONS FROM WORKER AGENT\n{"="*80}')
        logger.info(f'User ID: {user_id}')
        
        memory = self.get_memory(user_id)
        if not memory:
            logger.warning('No memory data received, returning None')
            return None
        
        # Extract recommendations from LTM
        ltm = memory.get('ltm', {})
        
        # Get recommendations, sleep_score, and confidence from LTM
        # They can be at the top level of LTM or in trends
        recommendations = ltm.get('recommendations', {})
        sleep_score = ltm.get('sleep_score')
        if sleep_score is None:
            sleep_score = ltm.get('trends', {}).get('avg_sleep_score')
        
        confidence = ltm.get('confidence')
        if confidence is None:
            confidence = ltm.get('trends', {}).get('confidence')
        
        personalized_tips = ltm.get('personalized_tips', [])
        
        # Get issues from LTM (saved directly) or extract from patterns
        issues = ltm.get('issues', [])
        
        # If no issues in LTM, try to extract from patterns (filter out non-issue patterns)
        if not issues:
            patterns = ltm.get('patterns', [])
            for pattern in patterns:
                if isinstance(pattern, dict):
                    pattern_type = pattern.get('type', '')
                    # Only include actual issues, not informational patterns
                    if pattern_type == 'issue' or 'problem' in pattern_type.lower() or 'warning' in pattern_type.lower():
                        issues.append(pattern.get('description', ''))
                elif isinstance(pattern, str):
                    if 'issue' in pattern.lower() or 'problem' in pattern.lower():
                        issues.append(pattern)
        
        result = {
            'sleep_score': sleep_score,
            'confidence': confidence,
            'issues': issues,
            'recommendations': recommendations,
            'personalized_tips': personalized_tips
        }
        
        # Log extracted recommendations
        try:
            result_str = json.dumps(result, indent=2)
            logger.info(f'\n{"="*80}\nEXTRACTED RECOMMENDATIONS:\n{"="*80}\n{result_str}\n{"="*80}')
        except Exception:
            logger.info(f'EXTRACTED RECOMMENDATIONS: {result}')
        
        return result

# Global worker client instance
worker_client = WorkerClient()

